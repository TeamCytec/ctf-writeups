## Web - Baby Web

- Solved by @Elession

- Flag: grey{0h_n0_mY_5up3r_53cr3t_4dm1n_fl4g}

We are given a login site and the source code.

![](./images/img1.png)

Based off the source code, there is a check for the session.
The site also uses `Flask` framework so we could assume that the cookie creation is based off that.

![](./images/img2.png)

After signing up and grabbing the session cookie, we can try to decode using `flask-unsign`

![](./images/img3.png)

In the source code, it checks for `is_admin` and the secret is also provided. We can then change the cookie values accordingly.

```python
app.secret_key = "baby-web"
```

![](./images/img4.png)

This is the result when we try to access the page with the new cookie.

![](./images/img5.png)

Upon inspecting the page further to look for clues, we notice this.

![](./images/img6.png)

There is a hidden button within the site.
We can just edit the html to remove the hidden function, which results in our flag.

![](./images/img7.png)