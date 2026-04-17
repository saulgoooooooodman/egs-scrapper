from actions.main_window_edit_actions import MainWindowEditActions
from actions.main_window_view_actions import MainWindowViewActions
from actions.main_window_data_actions import MainWindowDataActions


class MainWindowActions(
    MainWindowEditActions,
    MainWindowViewActions,
    MainWindowDataActions,
):
    pass