======
MDS QA
======

This page describes how to test MDS before a release.

Manual tests
############

Environment setup
=================

A private network with one MES 5.2 servers (i568 or x86_64) 
and one Windows XP or 7 client.

The network and the machines can of course be virtualized (it's
easy to setup with VirtualBox).

- The MES 5.2 server is a base installation from the DVD + all updates
- The mmc-wizard is installed on the server
- The private network will be 192.168.220.0/24 in this document
- The MES 5.2 server has a static IP of 192.168.220.10

Add the repo http://mes5devel.mandriva.com/iurt/jpbraun/iurt/mes5/i586/
to be able to get the MDS test packages :

  ::

  urpmi.addmedia jpbraun http://mes5devel.mandriva.com/iurt/jpbraun/iurt/mes5/i586/

Installation & configuration
============================

From the mmc-wizard (http://192.168.220.10/mmc-wizard/) select and install 
all MDS components.

- MDS domain: test.local
- MDS password: test$!
- SAMBA password: smbTest!
- Mail hostname: smtp.test.local
- Mail networks: 192.168.220.0/255.255.255.0
- DNS networks: 192.168.220.0/255.255.255.0

The configuration must be successfull.

MDS tests
=========

1. Login in MDS at http://192.168.220.10/mmc/ with root/test$!

2. Add a user:
   - Login: user1
   - Password: test1
   - Mail: user1@example.com

3. Edit the user and set some other fields:
   - Last name, phone, add secondary groups...

4. Add a second user:
   - Login: user2
   - Password: test2
   - Mail: user2@example.com
   - Alias: contact@example.com

5. Add the mail domain example.com

6. Login in roundcube (http://192.168.220.10/roundcubemail)
   with user1@example.com.
   - send a mail to user2@example.com
   - send a mail to contact@example.com

7. Login in rouncube with user2@example.com and check the mails

8. Edit the MMC ACLs of user1 and check "Change password"
   - Login the MMC with user1 and change his password

9. Create a DNS zone
   - FQDN: example.com
   - Server IP: 192.168.220.10
   - Network address: 192.168.220.0
   - Network mask: 24
   - Create DHCP subnet and reverse zone

10. Edit the DHCP subnet and add a dynamic pool from
    192.168.220.50 to 192.168.220.60

11. Restart both services in Network Services Management

12. Boot the Windows client and check if it gets an IP

13. Join the computer to the MES5DOMAIN domain (admin/smbTest!)

14. Login with user1 on the Windows client

15. Change user1 password on the Windows client

16. Login the MMC with user1 new password
