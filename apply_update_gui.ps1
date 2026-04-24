Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$payloadDir = Join-Path $scriptDir "payload"

function Get-VersionCodeFromFolder([string]$folderPath) {
    try {
        $versionFile = Join-Path $folderPath "version_info.py"
        if (-not (Test-Path $versionFile)) {
            return 0
        }
        $content = Get-Content -LiteralPath $versionFile -Raw -Encoding UTF8
        $match = [regex]::Match($content, 'APP_VERSION_CODE\s*=\s*(\d+)')
        if ($match.Success) {
            return [int]$match.Groups[1].Value
        }
    }
    catch {
    }
    return 0
}

function Ask-Confirm([string]$message) {
    return [System.Windows.Forms.MessageBox]::Show(
        $message,
        "EGS Scrapper Güncelleme",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Warning
    ) -eq [System.Windows.Forms.DialogResult]::Yes
}

function Show-Error([string]$message) {
    [System.Windows.Forms.MessageBox]::Show(
        $message,
        "EGS Scrapper Güncelleme",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
}

function Show-Info([string]$message) {
    [System.Windows.Forms.MessageBox]::Show(
        $message,
        "EGS Scrapper Güncelleme",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information
    ) | Out-Null
}

if (-not (Test-Path $payloadDir)) {
    Show-Error "Güncelleme paketinde payload klasörü bulunamadı."
    exit 1
}

$form = New-Object System.Windows.Forms.Form
$form.Text = "EGS Scrapper Güncelleme"
$form.Size = New-Object System.Drawing.Size(640, 255)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

$infoLabel = New-Object System.Windows.Forms.Label
$infoLabel.Location = New-Object System.Drawing.Point(16, 16)
$infoLabel.Size = New-Object System.Drawing.Size(590, 42)
$infoLabel.Text = "Kurulu EGS Scrapper klasörünü seçin. Araç önce uygulama dosyalarının yedeğini alır, sonra güncellemeyi uygular."
$form.Controls.Add($infoLabel)

$pathLabel = New-Object System.Windows.Forms.Label
$pathLabel.Location = New-Object System.Drawing.Point(16, 70)
$pathLabel.Size = New-Object System.Drawing.Size(120, 20)
$pathLabel.Text = "Kurulu Klasör:"
$form.Controls.Add($pathLabel)

$pathTextBox = New-Object System.Windows.Forms.TextBox
$pathTextBox.Location = New-Object System.Drawing.Point(16, 95)
$pathTextBox.Size = New-Object System.Drawing.Size(470, 24)
$pathTextBox.Text = (Join-Path $scriptDir "..\EGS Scrapper")
$form.Controls.Add($pathTextBox)

$browseButton = New-Object System.Windows.Forms.Button
$browseButton.Location = New-Object System.Drawing.Point(495, 93)
$browseButton.Size = New-Object System.Drawing.Size(95, 28)
$browseButton.Text = "Gözat"
$form.Controls.Add($browseButton)

$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Location = New-Object System.Drawing.Point(16, 135)
$statusLabel.Size = New-Object System.Drawing.Size(590, 42)
$statusLabel.Text = "Hazır"
$form.Controls.Add($statusLabel)

$updateButton = New-Object System.Windows.Forms.Button
$updateButton.Location = New-Object System.Drawing.Point(390, 180)
$updateButton.Size = New-Object System.Drawing.Size(95, 30)
$updateButton.Text = "Güncelle"
$form.Controls.Add($updateButton)

$closeButton = New-Object System.Windows.Forms.Button
$closeButton.Location = New-Object System.Drawing.Point(495, 180)
$closeButton.Size = New-Object System.Drawing.Size(95, 30)
$closeButton.Text = "Kapat"
$closeButton.Add_Click({ $form.Close() })
$form.Controls.Add($closeButton)

$browseButton.Add_Click({
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = "Kurulu EGS Scrapper klasörünü seçin"
    $dialog.SelectedPath = $pathTextBox.Text
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $pathTextBox.Text = $dialog.SelectedPath
    }
})

$updateButton.Add_Click({
    $targetDir = $pathTextBox.Text.Trim()
    if ([string]::IsNullOrWhiteSpace($targetDir)) {
        Show-Error "Önce kurulu klasörü seçin."
        return
    }

    if (-not (Test-Path $targetDir)) {
        Show-Error "Seçilen klasör bulunamadı."
        return
    }

    $exePath = Join-Path $targetDir "EGS Scrapper.exe"
    $appPyPath = Join-Path $targetDir "app.py"
    if (-not (Test-Path $exePath) -and -not (Test-Path $appPyPath)) {
        Show-Error "Seçilen klasör EGS Scrapper kurulumu gibi görünmüyor."
        return
    }

    $installedVersion = Get-VersionCodeFromFolder $targetDir
    $payloadVersion = Get-VersionCodeFromFolder $payloadDir

    if ($installedVersion -gt 0 -and $payloadVersion -gt 0) {
        if ($installedVersion -ge $payloadVersion) {
            $continueSame = Ask-Confirm "Seçilen kurulum zaten aynı sürümde veya daha yeni görünüyor.`n`nYine de üzerine yazmak istiyor musunuz?"
            if (-not $continueSame) {
                return
            }
        }
        elseif ($installedVersion -lt 10840) {
            $continueOld = Ask-Confirm "Seçilen kurulum çok eski bir sürüm görünüyor.`n`nGüncelleme yapılabilir; ancak eski veritabanı kayıtları otomatik yeniden parse edilmez. Güncellemeden sonra uygulama içinde ilgili günlerde `Veritabanını Güncelle` çalıştırmanız önerilir.`n`nDevam etmek istiyor musunuz?"
            if (-not $continueOld) {
                return
            }
        }
    }

    $updateButton.Enabled = $false
    $browseButton.Enabled = $false
    $statusLabel.Text = "Yedek hazırlanıyor..."
    $form.Refresh()

    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupDir = Join-Path $targetDir "update_backups"
        $backupFile = Join-Path $backupDir ("EGS_App_Backup_{0}.zip" -f $timestamp)

        if (-not (Test-Path $backupDir)) {
            New-Item -ItemType Directory -Path $backupDir | Out-Null
        }

        $items = Get-ChildItem -LiteralPath $targetDir -Force | Where-Object {
            $_.Name -notin @(
                "databases",
                "logs",
                "error_reports",
                "channel_dictionaries",
                "update_backups",
                "settings.json",
                "channel_rules.json",
                "common_dictionary.json"
            )
        }

        if (-not $items) {
            throw "Yedeklenecek uygulama dosyası bulunamadı."
        }

        Compress-Archive -Path $items.FullName -DestinationPath $backupFile -Force

        $statusLabel.Text = "Yeni dosyalar kopyalanıyor..."
        $form.Refresh()

        $null = robocopy $payloadDir $targetDir /E /NFL /NDL /NJH /NJS /NP
        $robocopyCode = $LASTEXITCODE
        if ($robocopyCode -ge 8) {
            throw "Güncelleme kopyalaması başarısız oldu. Robocopy kodu: $robocopyCode"
        }

        $statusLabel.Text = "Güncelleme tamamlandı."
        Show-Info("Güncelleme başarıyla tamamlandı.`n`nYedek dosyası:`n$backupFile`n`nNot: Çok eski bir sürümden geldiyseniz, program açıldıktan sonra ilgili günlerde `Veritabanını Güncelle` çalıştırmanız gerekebilir.")
    }
    catch {
        $statusLabel.Text = "Güncelleme başarısız oldu."
        Show-Error($_.Exception.Message)
    }
    finally {
        $updateButton.Enabled = $true
        $browseButton.Enabled = $true
    }
})

[void]$form.ShowDialog()
