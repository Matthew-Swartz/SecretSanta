import csv
import random
import sys, getopt
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def grab_csv(filename):
    data_hash = {}
    with open(filename, encoding='utf-8-sig', newline='') as csvfile:
        gift_data = csv.DictReader(csvfile)
        for row in gift_data:
            if row['active'] == 'TRUE':
                data_hash[row['userid']] = row
    return data_hash

def build_graph(family_hash):
    for k,v in family_hash.items():
        v.update(edge_to={x: family_hash[x] for x in family_hash if x.split('_')[0] not in v['immediate_family']}.keys())
    return family_hash

def determine_giver(family_hash):
    taken = []
    for k,v in family_hash.items():
        avaiable = list(v['edge_to'] - taken)
        gift_receiver = random.choice(avaiable)
        taken.append(gift_receiver)
        v.update(give_to=gift_receiver)
    return family_hash

def send_emails(family_hash, from_addr, password, whoopsie = 0):
    for k,v in family_hash.items():
        if v['email'] != '':
            to_addr = v['email']
            msg = MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = to_addr

            if whoopsie:
                msg['Subject'] = "O'Leary Family {} Secret Santa [DISREGARD PREVIOUS EMAIL]".format(datetime.today().year)
                body1 = "Whoops looks like someone's been pressing too many buttons.  Ignore that last email about who you've been paired with.\n"
                body2 = "Love, SantaBot"
                body = body1 + body2
            else:
                msg['Subject'] = "O'Leary Family {} Secret Santa Info".format(datetime.today().year)
                body1 = "Merry Christmas, " + v['name'] + "!\n"
                body2 = "This is an automated email letting you know that your {} Secret Santa gift recipient is {}.\n".format(datetime.today().year, family_hash[v['give_to']]['name'])
                body = body1 + body2

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_addr, password)
            text = msg.as_string()
            server.sendmail(from_addr, to_addr, text)
            server.quit()
            print("Email sent to " + v['name'])



def output_testing(family_hash):
    for k, v in family_hash.items():
        print(v['name'] + ' is giving a gift to ' + family_hash[v['give_to']]['name'])

def main(argv):
    deliver = 1
    whoopsie = 0
    csv_data = ''
    try:
        opts, args = getopt.getopt(argv, "hnwi:e:p:", ["help", "whoopsie", "file=", "email=", "password="])
    except getopt.GetoptError:
        print('SecretSanta.exe -i <inputfile> -e <email> -p <password>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('SecretSanta.exe -i <inputfile> -e <email> -p <password>')
            print('-i --file            name of the csv file containing Secret Santa info')
            print('-n [:no_deliver]     display pairings to console without sending emails')
            print('-e --email           input the address that will send out the pairing emails')
            print('-p --password        password of the email sending out the pairing emails')
            print('-w --whoopsie        use this command to email everyone to disregard the previous email')
            print('If you are experiencing issues sending emails, please make sure you are using a gmail address.')
            print('You may also have to enable less secure apps in your gmail settings')
            print('https://support.google.com/accounts/answer/6010255?hl=en')
            sys.exit()
        elif opt in ('-i', '--file'):
            csv_data = arg
        elif opt in ('-n'):
            deliver = 0
        elif opt in ('-e', '--email'):
            from_addr = arg
        elif opt in ('-p', '--password'):
            password = arg
        elif opt in ('-w', '--whoopsie'):
            whoopsie = 1

    if csv_data == '':
        print('Provide input file.\nsanta.py -i <inputfile> -n [:no_deliver]')
        sys.exit()

    family_hash = grab_csv(csv_data)
    family_hash = build_graph(family_hash)
    for x in range(0, 25):
        try:
            family_hash = determine_giver(family_hash)
        except Exception:
            pass
        else:
            break


    if deliver:
        send_emails(family_hash, from_addr, password, whoopsie)
    else:
        output_testing(family_hash)

if __name__ == '__main__':
    main(sys.argv[1:])