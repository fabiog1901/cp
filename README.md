# cp

Create some usernames

- `fabio`: admin
- `wanda`: read-write
- `ram`: read-only

The password is `London123` for all 3 accounts.

```sql
INSERT INTO public.users 
    (username,password_hash,salt,hash_algo,iterations,"role",attempts) 
VALUES 
    ('fabio',decode('7733A156C3F944A287725EB0CE985906F6C653E8DBE06E5B0A11D72A66085B56','hex'),decode('623A36F1B319239F4DDFBCE02E26E111','hex'),'sha256',100000,'admin',0),
    ('ram',decode('B0172B5EC16F3680CA0C1CD8CBCEA8E5AD4DBDB2292FA19ECFDC754C358CC6B9','hex'),decode('F92A4AD72B6FE991E453EB151BA2DFBE','hex'),'sha256',100000,'ro',0),
    ('wanda',decode('9F868852EF139BA0AEBC047B7180D4074F83A8E8A3BD876D8A3EA0C3BE2195C8','hex'),decode('2E862EC916D4C0920F1E061D0152A897','hex'),'sha256',100000,'rw',0)
;
```
