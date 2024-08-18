// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "../../interfaces/iface.sol";

// Reference: https://github.com/fbtc-com/fbtcX-contract/blob/main/src/LockedFBTC.sol
contract FBTCFacade is Initializable, OwnableUpgradeable {
    address public vault;
    address public lockedFBTC;

    receive() external payable {
        revert("value only accepted by the Vault contract");
    }

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address _vault, address _lockedFBTC) initializer public {
        __Ownable_init();

        vault = _vault;
        lockedFBTC = _lockedFBTC;
    }

    /**
     * @dev  mint lockedFBTC in response to a burn FBTC request on the FBTC bridge.
     */
    function mintLockedFbtcRequest(uint256 _amount) external onlyOwner {
        address fbtc = ILockedFBTC(lockedFBTC).fbtc();
        if (IERC20(fbtc).allowance(vault, lockedFBTC) < _amount) {
            bytes memory data = abi.encodeWithSelector(IERC20.approve.selector, lockedFBTC, _amount);
            IVault(vault).execute(fbtc, data, 0);
        }

        bytes memory data = abi.encodeWithSelector(ILockedFBTC.mintLockedFbtcRequest.selector, _amount);
        IVault(vault).execute(lockedFBTC, data, 0);
    }

    /**
     * @dev initiate a FBTC redemption request on the FBTC bridge with the corresponding BTC deposit tx details.
     */
    function redeemFbtcRequest(uint256 _amount, bytes32 _depositTxid, uint256 _outputIndex) external onlyOwner {
        bytes memory data = abi.encodeWithSelector(ILockedFBTC.redeemFbtcRequest.selector, _amount, _depositTxid, _outputIndex);
        IVault(vault).execute(lockedFBTC, data, 0);
    }

    /**
     * @dev burn Vault's locked FBTC and transfer back the equivalent FBTC to Vault.
     */
    function confirmRedeemFbtc(uint256 _amount) external onlyOwner {
        bytes memory data = abi.encodeWithSelector(ILockedFBTC.confirmRedeemFbtc.selector, _amount);
        IVault(vault).execute(lockedFBTC, data, 0);
    }

    /**
     * @dev burn Vault's lockedFBTC
     */
    function burn(uint256 _amount) external onlyOwner {
        bytes memory data = abi.encodeWithSelector(ILockedFBTC.burn.selector, _amount);
        IVault(vault).execute(lockedFBTC, data, 0);
    }
}