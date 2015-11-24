#!/usr/bin/env python3
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import socket
import random
import time
import shelve
import _pickle

#dealer class
class Dealer: 
    #init assigns everyone a set amount of resources
    def __init__(self, name):
        self.name = name
        #create unique save files for everyone
        f = shelve.open("{}.dat".format(self.name), flag="c", writeback=True)
        f["name"] = self.name
        #assign drugs for first time, or load existing file
        if not "inventory" in f:
            f["inventory"] = {}
            f["inventory"]["money"] = 500
            f["inventory"]["meth"] = 10
            f["inventory"]["heroin"] = 10
            f["inventory"]["cocaine"] = 10
            f.sync()
            self.inventory = {}
            self.inventory["money"] = 500
            self.inventory["meth"] = 10
            self.inventory["heroin"] = 10
            self.inventory["cocaine"] = 10
        else:
            self.inventory = f["inventory"]
        f.close()

    #sell function, writes to save file
    def sell(self, drug, price, amount):
        f = shelve.open("{}.dat".format(self.name), flag="c", writeback=True)
        if (int(f["inventory"][drug] >= 1)):
            f["inventory"][drug] -= int(amount)
            f["inventory"]["money"] += (int(amount) * int(price))
            drug_respond = str(drug)
            drug_respond_amount = str(f["inventory"][drug])
            drug_respond_cash = str(f["inventory"]["money"])
            #responds to channel, then syncs
            sendmsg(channel, ("You have " + drug_respond_amount + " " + str(drug) + " left, and $" + drug_respond_cash + " left"))
            f.sync()
            f.close()
        else:
            sendmsg(channel, "Not enough drugs")
    #buy function
    def buy(self, drug, price, amount):
        f = shelve.open("{}.dat".format(self.name), flag="c", writeback=True)
        if (int((f["inventory"]["money"])) >= (int(amount) * int(price))):
            f["inventory"][drug] += int(amount)
            f["inventory"]["money"] -= (int(amount) * int(price))
            drug_respond = str(drug)
            drug_respond_amount = str(f["inventory"][drug])
            drug_respond_cash = str(f["inventory"]["money"])
            #responds to channel, then syncs
            sendmsg(channel, ("You have " + drug_respond_amount + " " + str(drug) + " left, and $" + drug_respond_cash + " left"))
            f.sync()
            f.close()
        else:
            sendmsg(channel, "Not enough cash")

        
    #allows user to check amounts of resources
    def check_amount(self, drug):
        f = shelve.open("{}.dat".format(self.name), flag="c", writeback=True)
        if drug is "heroin":
            return(f["inventory"]['heroin'])
            f.sync()
            f.close()
        if drug is "cocaine":
            return(self.inventory['cocaine'])
            f.sync()
            f.close()
        if drug is "meth":
            return(self.inventory['meth'])
            f.sync()
            f.close()
        if drug is "money":
            return(self.inventory['money'])
            f.sync()
            f.close()
        else:
            return("Drug not specified")
            f.close()


#******** IRC SHIT *********

server = "irc.freenode.net"
channel = "#lainchan"
botnick = "drug-bot"
password = ""
#all bytes must be converted to UTF-8
def joinchan(chan): #channel join function
    ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8"))

#creates sockets, assigns nicks and usernames, and identifies
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667))
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick +" :connected\n", "UTF-8"))
ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8"))
ircsock.send(bytes("NICKSERV :IDENTIFY %s\r\n" % password, "UTF-8"))
#sleep for 2 to give server time to process
time.sleep(2)
joinchan(channel) #joins channel
readbuffer = ""
#main loop
while 1:
    #assigns random drug prices
    drug_price = random.randrange(5,15,1)
    #function to send messages to IRC channel
    def sendmsg(chan , msg):
        ircsock.send(bytes("PRIVMSG "+ chan +" :"+ msg +"\n", "UTF-8"))
    #creates a buffer to process the data
    readbuffer = readbuffer+ircsock.recv(1024).decode("UTF-8")
    #splits into lines then prints out in shell
    temp = str.split(readbuffer, "\n")
    print(readbuffer)
    readbuffer=temp.pop( )

    for line in temp:
        line = str.rstrip(line)
        line = str.split(line)
        try:
            #respond to pings
            if(line[0] == "PING"):
                ircsock.send(bytes("QUOTE :PONG %s\r\n" % line[1], "UTF-8"))
            #if it finds .sell, it calls the function from the drug user class
            if(line[3] == ":.sell"):
                #get name of person who called command
                sender = ""
                for char in line[0]:
                    if(char == "!"):
                        break
                    if(char != ":"):
                        sender += char
                #assigns player a save file
                current_player = Dealer(sender)
                #drug wanted
                drug_query = line[5]
                #amount of drug
                drug_amount = line[4]
                #calls the sell function from dealer class, passing in data collected above
                current_player.sell(drug_query, drug_price, drug_amount)
            if(line[3] == ":.buy"):
                #get name of person who called command
                sender = ""
                for char in line[0]:
                    if(char == "!"):
                        break
                    if(char != ":"):
                        sender += char
                #assigns player a save file
                current_player = Dealer(sender)
                #type of drug
                drug_query = line[5]
                #amount of drug
                drug_amount = line[4]
                #calls the buy function from dealer class, passing in data collected above
                current_player.buy(drug_query, drug_price, drug_amount)
            if(line[3] == ":.check"):
                sender = ""
                for char in line[0]:
                    if(char == "!"):
                        break
                    if(char != ":"):
                        sender += char

                current_player = Dealer(sender)
                requested_item = line[4]
                #returns the value of the requested item
                if requested_item:
                    if(requested_item == 'heroin'):
                        sendmsg(channel, (sender + ", you have " + str(current_player.check_amount('heroin')) + " heroin left" +"\n"))
                    elif(requested_item == 'meth'):
                        sendmsg(channel, (sender + ", you have " + str(current_player.check_amount('meth')) + " meth left" +"\n"))
                    elif(requested_item == 'money'):
                        sendmsg(channel, (sender + ", you have " + str(current_player.check_amount('money')) + " money left" +"\n" ))
                    elif(requested_item == 'cocaine'):
                        sendmsg(channel, (sender + ", you have " + str(current_player.check_amount('cocaine')) + " cocaine left" +"\n"))
                    else:
                        sendmsg(channel, ("Invalid option. Options for .check are heroin, meth, cocaine, or money"))
        except:
            continue







