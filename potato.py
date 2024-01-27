import csv
import os
import glob

from datetime import datetime, timedelta

myTwitchName = 'ldusoswa'

pitCrewCombined = []
crewChiefCombined = []
teamBossCombined = []
pitCrewYouTube = []
crewChiefYouTube = []
teamBossYouTube = []
twitchSubs = []
twitchPrimeExpiryBlurb = []
totalMemberCount = 0

totalGross = float(0)
totalPlatformCosts = float(0)
totalNet = float(0)

subListsDir = 'C:\\Users\\dusosl\\Downloads\\'

def find_recent_file(dir, prefix):
  # Get the list of all files in the directory
  file_list = glob.glob(dir + "/" + prefix + "*")

  # Sort the list of files by modification time
  file_list.sort(key=os.path.getmtime)

  # Return the most recent file
  return file_list[-1]

youtubeSubsFile = find_recent_file(subListsDir, 'Your members ')
twitchSubsFile = find_recent_file(subListsDir, 'subscriber-list')

# quick and dirty replace of poor imports or name change requests
def performTextReplacements(original):
    # Create a mapping of characters to replace
    mapping = {
        'ï¼‡': '\'',
        'Ã¼': 'ü'
    }

    for key, value in mapping.items():
        original = original.replace(key, value)

    return original

# TWITCH
with open(twitchSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row: row[1], reverse=False)
    if sortedlist[0][0] == myTwitchName:
        sortedlist.pop(0) # remove myself from Twitch

    for row in sortedlist:
        twitchSubs.append(performTextReplacements(row[0]))

        if row[5] == 'prime' or row[5] == 'gift':
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            currentDate = datetime.utcnow().strftime(date_format)
            subDate = row[1]

            daysLeft = 31 + (datetime.strptime(subDate, '%Y-%m-%dT%H:%M:%SZ') - datetime.strptime(currentDate, '%Y-%m-%dT%H:%M:%SZ')).days
            parsed_subscription_date = datetime.strptime(subDate, date_format)
            expiry_date = parsed_subscription_date + timedelta(days=31)
            formatted_expiry_date = expiry_date.strftime("%B %d, %Y at %I:%M %p")

            blurb = f'{performTextReplacements(row[0]).ljust(20)}\t{row[5]}\t\t{daysLeft}\t\t{formatted_expiry_date}'
            twitchPrimeExpiryBlurb.append(blurb)

# YouTube
with open(youtubeSubsFile, 'r') as csv_file:
    next(csv_file)
    reader = csv.reader(csv_file)
    sortedlist = sorted(reader, key=lambda row:float(row[4]), reverse=True)

    for row in sortedlist:
        if row[2] == "Pit Crew":
            pitCrewCombined.append(performTextReplacements(row[0]))
            pitCrewYouTube.append(performTextReplacements(row[0]))
        elif row[2] == "Crew Chief":
            crewChiefCombined.append(performTextReplacements(row[0]))
            crewChiefYouTube.append(performTextReplacements(row[0]))
        elif row[2] == "Team Boss":
            teamBossCombined.append(performTextReplacements(row[0]))
            teamBossYouTube.append(performTextReplacements(row[0]))

# output the complete list of names
print(f'\n#### All Members ####')
for member in teamBossCombined:
    print(member)

for member in crewChiefCombined:
    print(member)

print('\n')

for member in pitCrewCombined:
    print(member)

for member in twitchSubs:
    print(member)

totalMemberCount = len(pitCrewCombined) + len(crewChiefCombined) + len(teamBossCombined) + len(twitchSubs)

# TODO print out youtube description blurb
print(f'\nTeam Boss (€19.99/mo)\t\t{", ".join(teamBossCombined)}')
print(f'Crew Chief (€9.99/mo)\t\t{", ".join(crewChiefCombined)}')
print(f'Pit Crew (€4.99/mo)\t\t{", ".join(pitCrewCombined)}')
print(f'TWITCH (€4.99/mo)\t\t{", ".join(twitchSubs)}')

# Create the csv for photoshop to import
def formatForPhotoshopText(membersArray, padding):
    photoshopText = ''
    for index, member in enumerate(membersArray):
            photoshopText = f'{photoshopText} {member.ljust(padding)}'

    return photoshopText

data = [
    ['teamBoss', 'crewChief', 'pitCrew', 'twitchSubs'],
    [
        formatForPhotoshopText(teamBossCombined, 38),
        formatForPhotoshopText(crewChiefCombined, 35),
        formatForPhotoshopText(pitCrewCombined, 36),
        formatForPhotoshopText(twitchSubs, 30)
    ]
]
psdName = 'levels.csv'

with open(psdName, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    for row in data:
        writer.writerow(row)

    print(f'\nCSV file created successfully for Photoshop import: {psdName}')

def calculateAndOutputTotals(platform, tierName, members, pricePerMonth):
    # Calculate totals for this tier
    monthlyGross = len(members)*pricePerMonth
    # calculate the platform costs
    if platform == 'YouTube':
        monthlyPlatformFees = monthlyGross*30/100
    elif platform == 'Twitch':
        monthlyPlatformFees = monthlyGross*50/100
    elif platform == 'Patreon':
        if pricePerMonth < 3:
            monthlyPlatformFees = monthlyGross*5/100 + len(members)*0.10
        else:
            monthlyPlatformFees = monthlyGross*2.9/100 + len(members)*0.30
    else:
        monthlyPlatformFees = 0
    monthlyNet = monthlyGross - monthlyPlatformFees

    # Update running totals
    global totalGross
    global totalPlatformCosts
    global totalNet
    totalGross += monthlyGross
    totalPlatformCosts += monthlyPlatformFees
    totalNet += monthlyNet

    # spit out the data
    if len(members) > 0:
        print(f'{platform} - {tierName}\t{len(members)}\t€{pricePerMonth}\t€{"{:.2f}".format(monthlyGross)}\t\t€{"{:.2f}".format(monthlyPlatformFees)}\t\t€{"{:.2f}".format(monthlyNet)}')

# Do earnings projections
print(f'\n############################# MONTHLY EARNINGS REPORT #####################################')
print(f'level\t\t\tmembers\trate\tgross income\tplatform costs\ttotal (before tax)')
print(f'_____________________\t______\t______\t______________\t______________\t__________________')
calculateAndOutputTotals('YouTube', 'Team Boss', teamBossYouTube, 19.99)
calculateAndOutputTotals('YouTube', 'Crew Chief', crewChiefYouTube, 9.99)
calculateAndOutputTotals('YouTube', 'Pit Crew', pitCrewYouTube, 4.99)
calculateAndOutputTotals('Twitch', 'Subscriptions', twitchSubs, 4.99)

print('===========================================================================================')
print(f'TOTAL\t\t\t{totalMemberCount}\t\t€{"{:.2f}".format(totalGross)}\t\t€{"{:.2f}".format(totalPlatformCosts)}\t\t€{"{:.2f}".format(totalNet)}')
print(f'###########################################################################################')

print(f'\n\n############################# TWITCH PRIME EXPIRING SOON #####################################')
print(f'member\t\t\tsub type\tdays left\t\texpiry date')
print(f'_____________________\t__________\t__________\t___________________________')
for blurb in twitchPrimeExpiryBlurb:
    print(blurb)
print(f'\nTwitch prime subs do not auto-renew. If you\'d like to renew your prime sub, the easiest way \nto remember to renew it is by setting a monthly reminder for the expiry date beside your name')
print('##############################################################################################')
