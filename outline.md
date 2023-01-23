_How it works:_
-
- setting up a logging file to track what emails are being deleted every day
- With SCOPES you get the read and write privileges to the mail inbox
- With SERVICE you acces the mailbox
- The init() function checks your credentials for accessing the mailbox and storing the Email tokens
- the search() function checks the Emails for a match with the query specifying what Emails should be spam
- the delete_messages() function deletes the Emails that matched the query in the search() function
