param(
	[string]$Name = "FarmManager",
	[string]$IconPath = ""
)

if (-not (Test-Path .venv)) {
	python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

$iconArg = ""
if ($IconPath -and (Test-Path $IconPath)) {
	$iconArg = "--icon `"$IconPath`""
}

pyinstaller --noconfirm --clean --windowed --name $Name $iconArg `
	--exclude-module tests `
	--add-data "app\assets;app\assets" `
	main.py

Write-Host "Build terminé. Binaire dans dist\$Name\$Name.exe"

