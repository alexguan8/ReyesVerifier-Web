#...................................
# DEPLOYMENT READY- No Identity Column
#...................................	This script is for Alphabetical Name ranges for load

$LogFile = "C:\Users\aguan\Downloads\ActiveSync_AC\MDI_ACTIVESYNC_LOG.txt" #"\\rhcorp\Business Intelligence\ETL\logs\Powershell\prod\MDI_ACTIVESYNC_LOG.TXT"

#Function that logs a message to a text file
function LogMessage
{
    param([string]$Message)
    
    ((Get-Date).ToString() + " - " + $Message) >> $LogFile;
}

LogMessage -Message "Logging in"

#$username = "rh\svc_cognosactivesync"
#$mypassword = "ChevyHeavy1234!"

$username = "aguan"
$mypassword = "Welcome8576!"

$outputfile = "C:\Powershell\SourceData\activesyncdevices_AC.csv"
#$outputfile = "\\rhcorp\Business Intelligence\Data Sources\RH Corp\Mobile Device\activesyncdevices.csv"
$ConnectionUri ="http://spexchdb321.reyesholdings.com/PowerShell/"

$secpasswd = ConvertTo-SecureString $mypassword -AsPlainText -Force
$UserCredential = New-Object System.Management.Automation.PSCredential ($username, $secpasswd)

$now = Get-Date											#Used for timestamps
$date = $now.ToShortDateString()						#Short date format for email message subject

$report = @()

$stats = @("DeviceID",
            "DeviceIMEI",
            "DeviceAccessState",
            "DeviceAccessStateReason",
            "DeviceModel"
            "DeviceType",
            "DeviceFriendlyName",
            "DeviceOS",
            "DeviceOSLanguage",
            "LastSyncAttemptTime",
            "LastSuccessSync",
            "FirstSyncTime",
            "DeviceUserAgent",
            "DevicePhoneNumber",
            "DeviceMobileOperator",
            "Guid",
            "DeviceActiveSyncVersion",
            "LastPolicyUpdateTime",
            "IsValid",
            "ObjectState",
            "ClientType",
            "NumberOfFoldersSynced",
            "DevicePolicyApplicationStatus",
            "DevicePolicyApplied"

          )

$reportemailsubject = "Exchange ActiveSync Device Report - $date"
$myDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$reportfile = "$myDir\ExchangeActiveSyncDeviceReport.csv"



#...................................
# Initialize
#...................................


#Add Exchange 2010/2013 snapin if not already loaded in the PowerShell session
if (!(Get-PSSnapin | where {$_.Name -eq "Microsoft.Exchange.Management.PowerShell.E2010"}))
{
	try
	{
   $Session = New-PSSession –ConfigurationName Microsoft.Exchange –ConnectionUri $ConnectionURI -Credential $UserCredential
   Import-PSSession $Session -AllowClobber -DisableNameChecking
   Write-Output "Successfully logged in with username $($username)"
   LogMessage -Message "Successfully logged in with username $($username)"
    }
	catch
	{
        #Snapin was not loaded
        Write-Output "Invalid credentials with username $($username)"
		Write-Warning $_.Exception.Message
		EXIT
	}
	#. $env:ExchangeInstallPath\bin\RemoteExchange.ps1
	#Connect-ExchangeServer -auto -AllowClobber
}

LogMessage -Message "JOB END"


