@echo off
chcp 65001 >nul
title EGS Scrapper - Projeyi Klasorlere Ayir

cd /d "%~dp0"

echo ==========================================
echo   EGS SCRAPPER DOSYA DUZENLEME ARACI
echo ==========================================
echo.
echo Bu islem:
echo - klasorleri olusturur
echo - dosyalari ilgili klasorlere tasir
echo - ayni isimli hedef dosya varsa ustune yazmaz
echo.
echo Devam etmeden once proje klasorunun yedegini alman onerilir.
echo.
pause

echo.
echo [1/4] Klasorler olusturuluyor...
if not exist "ui" mkdir "ui"
if not exist "actions" mkdir "actions"
if not exist "data" mkdir "data"
if not exist "parsing" mkdir "parsing"
if not exist "dictionaries" mkdir "dictionaries"
if not exist "dialogs" mkdir "dialogs"
if not exist "core" mkdir "core"
if not exist "watchers" mkdir "watchers"
if not exist "models" mkdir "models"

if not exist "ui\__init__.py" type nul > "ui\__init__.py"
if not exist "actions\__init__.py" type nul > "actions\__init__.py"
if not exist "data\__init__.py" type nul > "data\__init__.py"
if not exist "parsing\__init__.py" type nul > "parsing\__init__.py"
if not exist "dictionaries\__init__.py" type nul > "dictionaries\__init__.py"
if not exist "dialogs\__init__.py" type nul > "dialogs\__init__.py"
if not exist "core\__init__.py" type nul > "core\__init__.py"
if not exist "watchers\__init__.py" type nul > "watchers\__init__.py"
if not exist "models\__init__.py" type nul > "models\__init__.py"

echo Tamam.
echo.

echo [2/4] Dosyalar tasiniyor...
call :move_if_exists "main_window_ui.py" "ui\main_window_ui.py"
call :move_if_exists "main_window_topbar.py" "ui\main_window_topbar.py"
call :move_if_exists "main_window_filters.py" "ui\main_window_filters.py"
call :move_if_exists "main_window_preview.py" "ui\main_window_preview.py"
call :move_if_exists "main_window_menu_builder.py" "ui\main_window_menu_builder.py"
call :move_if_exists "main_window_context_menus.py" "ui\main_window_context_menus.py"

call :move_if_exists "main_window_actions.py" "actions\main_window_actions.py"
call :move_if_exists "main_window_edit_actions.py" "actions\main_window_edit_actions.py"
call :move_if_exists "main_window_view_actions.py" "actions\main_window_view_actions.py"
call :move_if_exists "main_window_data_actions.py" "actions\main_window_data_actions.py"
call :move_if_exists "main_window_state_hooks.py" "actions\main_window_state_hooks.py"

call :move_if_exists "database.py" "data\database.py"
call :move_if_exists "database_core.py" "data\database_core.py"
call :move_if_exists "database_search.py" "data\database_search.py"
call :move_if_exists "database_merge.py" "data\database_merge.py"
call :move_if_exists "cache_manager.py" "data\cache_manager.py"

call :move_if_exists "parser.py" "parsing\parser.py"
call :move_if_exists "scanner.py" "parsing\scanner.py"
call :move_if_exists "news_worker.py" "parsing\news_worker.py"
call :move_if_exists "worker_manager.py" "parsing\worker_manager.py"

call :move_if_exists "title_spellcheck.py" "dictionaries\title_spellcheck.py"
call :move_if_exists "dictionary_store.py" "dictionaries\dictionary_store.py"
call :move_if_exists "spell_backend.py" "dictionaries\spell_backend.py"
call :move_if_exists "title_transform.py" "dictionaries\title_transform.py"

call :move_if_exists "archive_search_dialog.py" "dialogs\archive_search_dialog.py"
call :move_if_exists "startup_dialog.py" "dialogs\startup_dialog.py"
call :move_if_exists "find_replace_dialog.py" "dialogs\find_replace_dialog.py"
call :move_if_exists "code_filter_wizard.py" "dialogs\code_filter_wizard.py"
call :move_if_exists "help_dialog.py" "dialogs\help_dialog.py"
call :move_if_exists "info_dialog.py" "dialogs\info_dialog.py"
call :move_if_exists "log_viewer_dialog.py" "dialogs\log_viewer_dialog.py"
call :move_if_exists "rules_manager_dialog.py" "dialogs\rules_manager_dialog.py"
call :move_if_exists "title_dictionary_manager.py" "dialogs\title_dictionary_manager.py"
call :move_if_exists "dictionary_bundle_dialog.py" "dialogs\dictionary_bundle_dialog.py"
call :move_if_exists "external_db_manager.py" "dialogs\external_db_manager.py"
call :move_if_exists "db_merge_dialog.py" "dialogs\db_merge_dialog.py"

call :move_if_exists "app_paths.py" "core\app_paths.py"
call :move_if_exists "settings_manager.py" "core\settings_manager.py"
call :move_if_exists "logger_setup.py" "core\logger_setup.py"
call :move_if_exists "rules_store.py" "core\rules_store.py"
call :move_if_exists "text_utils.py" "core\text_utils.py"
call :move_if_exists "window_state_manager.py" "core\window_state_manager.py"

call :move_if_exists "live_reload.py" "watchers\live_reload.py"

call :move_if_exists "news_table_model.py" "models\news_table_model.py"
call :move_if_exists "news_list_model.py" "models\news_list_model.py"

echo.
echo [3/4] Tamamlayici kontrol...
if exist "main_window.py" echo main_window.py yerinde
if exist "app.py" echo app.py yerinde
if exist "version_info.py" echo version_info.py yerinde
if exist "health_check.py" echo health_check.py yerinde
if exist "saglik_kontrolu.bat" echo saglik_kontrolu.bat yerinde

echo.
echo [4/4] Islem tamamlandi.
echo.
echo Sonraki adim:
echo 1- Import yollarini yeni klasor yapisina gore guncelle
echo 2- saglik_kontrolu.bat calistir
echo.
pause
exit /b 0


:move_if_exists
set "SRC=%~1"
set "DST=%~2"

if not exist "%SRC%" (
    echo [YOK] %SRC%
    goto :eof
)

if exist "%DST%" (
    echo [ATLANDI - HEDEF VAR] %SRC% ^> %DST%
    goto :eof
)

move "%SRC%" "%DST%" >nul
if errorlevel 1 (
    echo [HATA] %SRC% tasinamadi
) else (
    echo [TASINDI] %SRC% ^> %DST%
)
goto :eof