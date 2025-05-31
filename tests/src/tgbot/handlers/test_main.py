# type: ignore
"""Unit tests for src/tgbot/handlers/main.py"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from typing import Any, Callable, cast, Type, TypeAlias
from unittest.mock import call, MagicMock

import pytest
from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.utils.magic_filter import MagicFilter
from pytest_mock import MockerFixture

from tgbot.handlers.errors import ErrHandler
from tgbot.handlers.main import MainHandler
from tgbot.misc.filters import IsAdmin


__all__: tuple = ()


FilterType: TypeAlias = Type[Command] | Type[MagicFilter] | MagicMock
FilterConfig: TypeAlias = tuple[FilterType, dict[str, Any]]
HandlerSetup: TypeAlias = tuple[Callable[..., Any], list[FilterConfig]]

MODULE_PATH_PREFIX = "tgbot.handlers.main"


# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init
class TestMainHandler:
    """Unit tests for MainHandler class."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker: MockerFixture) -> None:
        """
        Fixture to set up mocks for testing MainHandler.

        :param mocker: Pytest mocker fixture used to patch and create mocks.
        :return: None
        """
        self.mock_config: MagicMock = MagicMock()
        self.mock_config.admins = [123, 456]
        self.mock_dp: MagicMock = MagicMock(spec=Dispatcher)
        self.mock_tmpl: MagicMock = MagicMock()
        self.mock_kb: MagicMock = MagicMock()
        self.mock_is_admin: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.IsAdmin")
        self.mock_is_admin_instance: MagicMock = MagicMock(spec=IsAdmin)
        self.mock_is_admin.return_value = self.mock_is_admin_instance
        # Mocks for Services
        self.mock_admin_service: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.AdminService")
        self.mock_admin_svc_instance: MagicMock = MagicMock()
        self.mock_admin_service.return_value = self.mock_admin_svc_instance
        self.mock_base_service: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.BaseService")
        self.mock_base_svc_instance: MagicMock = MagicMock()
        self.mock_base_service.return_value = self.mock_base_svc_instance
        self.mock_profile_service: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.ProfileService")
        self.mock_profile_svc_instance: MagicMock = MagicMock()
        self.mock_profile_service.return_value = self.mock_profile_svc_instance
        self.mock_setting_sservice: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.SettingsService")
        self.mock_settings_svc_instance: MagicMock = MagicMock()
        self.mock_setting_sservice.return_value = self.mock_settings_svc_instance
        # Mocks for Handlers
        self.mock_admin_handler: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.AdminHandler")
        self.mock_admin_hdlr_instance: MagicMock = MagicMock()
        self.mock_admin_handler.return_value = self.mock_admin_hdlr_instance
        self.mock_common_handler: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.CommonHandler")
        self.mock_common_hdlr_instance: MagicMock = MagicMock()
        self.mock_common_handler.return_value = self.mock_common_hdlr_instance
        self.mock_profile_handler: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.ProfileHandler")
        self.mock_profile_hdlr_instance: MagicMock = MagicMock()
        self.mock_profile_handler.return_value = self.mock_profile_hdlr_instance
        self.mock_settings_handler: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.SettingsHandler")
        self.mock_settings_hdlr_instance: MagicMock = MagicMock()
        self.mock_settings_handler.return_value = self.mock_settings_hdlr_instance
        # Mocks for Router
        self.mock_router: MagicMock = mocker.patch(f"{MODULE_PATH_PREFIX}.Router")
        self.mock_private_router: MagicMock = MagicMock(spec=Router)
        self.mock_private_router.message = MagicMock()
        self.mock_private_router.message.register = MagicMock()
        self.mock_private_router.message.filter = MagicMock()
        self.mock_private_router.errors = MagicMock()
        self.mock_private_router.errors.register = MagicMock()
        self.mock_router.return_value = self.mock_private_router

    def test_initialization(self) -> None:
        """
        Test that MainHandler initializes its components correctly.

        :return: None
        """
        main_handler: MainHandler = MainHandler(
            config=self.mock_config, dp=self.mock_dp, tmpl=self.mock_tmpl, kb=self.mock_kb
        )
        self.mock_is_admin.assert_called_once_with(admins_ids=self.mock_config.admins)
        assert main_handler._is_admin == self.mock_is_admin_instance
        self.mock_admin_service.assert_called_once_with(config=self.mock_config, tmpl=self.mock_tmpl, kb=self.mock_kb)
        self.mock_base_service.assert_called_once_with(config=self.mock_config, tmpl=self.mock_tmpl, kb=self.mock_kb)
        self.mock_profile_service.assert_called_once_with(config=self.mock_config, tmpl=self.mock_tmpl, kb=self.mock_kb)
        self.mock_setting_sservice.assert_called_once_with(
            config=self.mock_config, tmpl=self.mock_tmpl, kb=self.mock_kb
        )
        self.mock_admin_handler.assert_called_once_with(service=self.mock_admin_svc_instance)
        self.mock_common_handler.assert_called_once_with(service=self.mock_base_svc_instance)
        self.mock_profile_handler.assert_called_once_with(service=self.mock_profile_svc_instance)
        self.mock_settings_handler.assert_called_once_with(service=self.mock_settings_svc_instance)

    # noinspection PyUnresolvedReferences
    def test_register_handlers_argument_check(self) -> None:
        """
        Test that _register_handlers registers handlers with correct arguments and order.

        :return: None
        """
        MainHandler(config=self.mock_config, dp=self.mock_dp, tmpl=self.mock_tmpl, kb=self.mock_kb)
        self.mock_router.assert_called_once_with(name="Private chat")
        # Checking the router filter
        router_filter_call: call | None = self.mock_private_router.message.filter.call_args
        assert router_filter_call is not None, "Router.message.filter was not called"
        actual_router_filter_arg: MagicFilter = cast(MagicFilter, router_filter_call.args[0])
        expected_router_magic_filter: MagicFilter = F.chat.type == "private"
        assert isinstance(actual_router_filter_arg, MagicFilter)
        # Compare magic_data, as this captures the essence of the filter
        assert actual_router_filter_arg.magic_data == expected_router_magic_filter.magic_data, (
            f"Router filter mismatch. "
            f"Expected data {expected_router_magic_filter.magic_data}, got {actual_router_filter_arg.magic_data}"
        )
        self.mock_dp.include_router.assert_called_once_with(router=self.mock_private_router)
        registrations: list[call] = self.mock_private_router.message.register.call_args_list
        expected_handler_setups: list[HandlerSetup] = [
            (  # command /start
                self.mock_profile_hdlr_instance.cmd_start,
                [(Command, {"commands": ("start",)}), (MagicFilter, {"magic_data": (F.text == "/start").magic_data})],
            ),
            (  # command /help
                self.mock_profile_hdlr_instance.cmd_help,
                [(Command, {"commands": ("help",)})],
            ),
            (  # command /settings
                self.mock_settings_hdlr_instance.cmd_or_msg_settings,
                [(Command, {"commands": ("settings",)})],
            ),
            (  # command /admin
                self.mock_admin_hdlr_instance.cmd_admin,
                [(Command, {"commands": ("admin",)}), (self.mock_is_admin_instance, {})],  # Здесь MagicMock
            ),
            (  # delete unhandled messages
                self.mock_common_hdlr_instance.any_delete,
                [(MagicFilter, {"magic_data": (~F.text | F.text).magic_data})],
            ),
        ]
        assert len(registrations) == len(expected_handler_setups), (
            f"Expected {len(expected_handler_setups)} message handler registrations, "
            f"got {len(registrations)}. Actual calls: {registrations}"
        )
        for i, (expected_handler, expected_filters_config) in enumerate(expected_handler_setups):
            actual_call: call = registrations[i]
            actual_call_args: tuple[Any, ...] = actual_call.args  # Get the tuple of call arguments
            # 1. Check the handler itself (first argument)
            actual_handler_arg: Callable[..., Any] = actual_call_args[0]
            assert (
                actual_handler_arg == expected_handler
            ), f"Registration {i}: Handler mismatch. Expected {expected_handler}, got {actual_handler_arg}"
            # 2. Checking filters (other arguments)
            # The actual filters will be instances of Command, MagicFilter, or MagicMock (for IsAdmin)
            actual_filter_args: tuple[Command | MagicFilter | MagicMock, ...] = actual_call_args[1:]
            assert len(actual_filter_args) == len(expected_filters_config), (
                f"Registration {i} for {expected_handler}: Number of filters mismatch. "
                f"Expected {len(expected_filters_config)}, got {len(actual_filter_args)}. "
                f"Actual filters: {actual_filter_args}"
            )
            for j, (expected_filter_type_or_instance, expected_attrs) in enumerate(expected_filters_config):
                actual_filter_obj: Command | MagicFilter | MagicMock = actual_filter_args[j]
                if isinstance(expected_filter_type_or_instance, MagicMock):
                    # If a specific mock instance (like self.mock_is_admin_instance) is expected.
                    assert actual_filter_obj == expected_filter_type_or_instance, (
                        f"Registration {i}, Filter {j}: Mock instance mismatch. "
                        f"Expected {expected_filter_type_or_instance}, got {actual_filter_obj}"
                    )
                else:
                    # expected_filter_type_or_instance здесь будет Type[Command] или Type[MagicFilter]
                    # If a filter type is expected (Command, MagicFilter)
                    expected_type_to_check: Type[Command | MagicFilter] = cast(
                        Type[Command] | Type[MagicFilter], expected_filter_type_or_instance
                    )
                    assert isinstance(actual_filter_obj, expected_type_to_check), (
                        f"Registration {i}, Filter {j}: Type mismatch. "
                        f"Expected instance of {expected_type_to_check}, got {type(actual_filter_obj)}"
                    )
                    for attr_name, expected_value in expected_attrs.items():
                        actual_value: Any = getattr(actual_filter_obj, attr_name)
                        assert actual_value == expected_value, (
                            f"Registration {i}, Filter {j} ({expected_type_to_check.__name__}): "
                            f"Attribute '{attr_name}' mismatch. "
                            f"Expected {repr(expected_value)}, got {repr(actual_value)}"
                        )
        # Checking error handler registration
        self.mock_private_router.errors.register.assert_called_once_with(ErrHandler)
