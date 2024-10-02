// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts/utils/Address.sol";

import "../interfaces/IMintableContract.sol";
import "../interfaces/ISupplyFeeder.sol";

contract VaultWithoutNative is Initializable, AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    using SafeERC20 for IERC20;
    using Address for address;

    address private _DEPRECATED_WBTC_;
    address public uniBTC;

    mapping(address => uint256) public caps;
    mapping(address => bool) public paused;

    bool private _DEPRECATED_redeemable_;

    address private constant NATIVE_BTC = address(0xbeDFFfFfFFfFfFfFFfFfFFFFfFFfFFffffFFFFFF);
    uint8 private constant _DEPRECATED_L2_BTC_DECIMAL_ = 18;

    uint256 public constant EXCHANGE_RATE_BASE = 1e10;

    address public supplyFeeder;
    //================== 2024/09/30 ===========
    mapping(address => bool) public allowedTokenList;
    mapping(address => bool) public allowedTargetList;
    bool public outOfService;

    receive() external payable {}

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    modifier serviceNormal{
        require(!outOfService, "SYS011");
        _;
    }

    /**
     * @dev mint uniBTC with the given type of wrapped BTC
     */
    function mint(address _token, uint256 _amount) external serviceNormal {
        require(allowedTokenList[_token] && !paused[_token], "SYS002");
        _mint(msg.sender, _token, _amount);
    }

    // @dev execute a contract call that also transfers '_value' wei to '_target'
    function execute(address _target, bytes memory _data, uint256 _value) external nonReentrant onlyRole(OPERATOR_ROLE) serviceNormal returns (bytes memory) {
        require(allowedTargetList[_target], "SYS001");
        return _target.functionCallWithValue(_data, _value);
    }

    /**
     * ======================================================================================
     *
     * ADMIN
     *
     * ======================================================================================
     */
    function initialize(address _defaultAdmin, address _uniBTC) initializer public {
        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();

        require(_uniBTC != address(0x0), "SYS001");

        _grantRole(DEFAULT_ADMIN_ROLE, _defaultAdmin);
        _grantRole(PAUSER_ROLE, _defaultAdmin);

        uniBTC = _uniBTC;
    }

    /**
     * @dev allow the minting of a token
     */
    function allowToken(address[] memory _token) external onlyRole(DEFAULT_ADMIN_ROLE) {
        for (uint256 i = 0; i < _token.length; i++) {
            allowedTokenList[_token[i]] = true;
        }
        emit TokenAllowed(_token);
    }

    /**
     * @dev deny the minting of a token
     */
    function denyToken(address[] memory _token) external onlyRole(DEFAULT_ADMIN_ROLE) {
        for (uint256 i = 0; i < _token.length; i++) {
            allowedTokenList[_token[i]] = false;
        }
        emit TokenDenied(_token);
    }

    /**
     * @dev allow the target address
     */
    function allowTarget(address[] memory _targets) external onlyRole(DEFAULT_ADMIN_ROLE) {
        for (uint256 i = 0; i < _targets.length; i++) {
            allowedTargetList[_targets[i]] = true;
        }
        emit TargetAllowed(_targets);
    }

    /**
     * @dev deny the target address
     */
    function denyTarget(address[] memory _targets) external onlyRole(DEFAULT_ADMIN_ROLE) {
        for (uint256 i = 0; i < _targets.length; i++) {
            allowedTargetList[_targets[i]] = false;
        }
        emit TargetDenied(_targets);
    }

    /**
     * @dev a pauser pause the minting of a token
     */
    function pauseToken(address[] memory _tokens) external onlyRole(PAUSER_ROLE) {
        for (uint256 i = 0; i < _tokens.length; i++) {
            paused[_tokens[i]] = true;
        }
        emit TokenPaused(_tokens);
    }

    /**
     * @dev a pauser unpause the minting of a token
     */
    function unpauseToken(address[] memory _tokens) external onlyRole(PAUSER_ROLE) {
        for (uint256 i = 0; i < _tokens.length; i++) {
            paused[_tokens[i]] = false;
        }
        emit TokenUnpaused(_tokens);
    }

    /**
     * @dev toggle service
     */
    function startService() external onlyRole(PAUSER_ROLE) {
        outOfService = false;
        emit StartService();
    }

    /**
 * @dev toggle service
     */
    function stopService() external onlyRole(PAUSER_ROLE) {
        outOfService = true;
        emit StopService();
    }

    /**
     * @dev set cap for a specific type of wrapped BTC
     */
    function setCap(address _token, uint256 _cap) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_token != NATIVE_BTC, "SYS012");
        require(_token != address(0x0), "SYS003");
        require(_cap > 0, "USR017");

        uint8 decs = ERC20(_token).decimals();

        require(decs == 8 || decs == 18, "SYS004");

        caps[_token] = _cap;
    }

    /**
     * @dev set the supply feeder address to track the asset supply for the vault
     */
    function setSupplyFeeder(address _supplyFeeder) external onlyRole(DEFAULT_ADMIN_ROLE) {
        supplyFeeder = _supplyFeeder;
    }

    /**
     * ======================================================================================
     *
     * INTERNAL
     *
     * ======================================================================================
     */

    /**
     * @dev mint uniBTC with wrapped BTC tokens
     */
    function _mint(address _sender, address _token, uint256 _amount) internal {
        (, uint256 uniBTCAmount) = _amounts(_token, _amount);
        require(uniBTCAmount > 0, "USR010");

        uint256 totalSupply = ISupplyFeeder(supplyFeeder).totalSupply(_token);
        require((totalSupply + _amount <= caps[_token]) && caps[_token] != 0, "USR003");

        IERC20(_token).safeTransferFrom(_sender, address(this), _amount);
        IMintableContract(uniBTC).mint(_sender, uniBTCAmount);

        emit Minted(_token, _amount);
    }

    /**
     * @dev determine the valid wrapped BTC amount and the corresponding uniBTC amount.
     */
    function _amounts(address _token, uint256 _amount) internal view returns (uint256, uint256) {
        uint8 decs = ERC20(_token).decimals();
        if (decs == 8) return (_amount, _amount);
        if (decs == 18) {
            uint256 uniBTCAmt = _amount / EXCHANGE_RATE_BASE;
            return (uniBTCAmt * EXCHANGE_RATE_BASE, uniBTCAmt);
        }
        return (0, 0);
    }

    /**
     * ======================================================================================
     *
     * EVENTS
     *
     * ======================================================================================
     */
    event Minted(address token, uint256 amount);
    event TokenPaused(address[] token);
    event TokenUnpaused(address[] token);
    event TokenAllowed(address[] token);
    event TokenDenied(address[] token);
    event TargetAllowed(address[] token);
    event TargetDenied(address[] token);
    event StartService();
    event StopService();
}
