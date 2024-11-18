Add-Type -AssemblyName System.Windows.Forms

$current_location = Get-Location

$root_folder = "C:/your/root/folder"

# Create OpenFileDialog object
$openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
$openFileDialog.Filter = "Image Files (*.jpg;*.jpeg;*.png)|*.jpg;*.jpeg;*.png|All Files (*.*)|*.*"
$openFileDialog.Title = "Select Images"
$openFileDialog.Multiselect = $true

# Show dialog and process results
if ($openFileDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    $selectedFiles = $openFileDialog.FileNames

    # Process each file in a subshell
    foreach ($file in $selectedFiles) {
        # Quote the file path to handle spaces
        $quotedFile = "`"$file`""

        Start-Process -NoNewWindow -Wait -FilePath "cmd.exe" -ArgumentList "/c `"$root_folder\env\Scripts\activate && py $root_folder\main.py $quotedFile && deactivate.bat`""
    }
} else {
    Write-Output "No files were selected."
}

Set-Location $current_location
