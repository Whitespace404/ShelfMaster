Exec `ipconfig` on cmd
get ipv4 adress


run the flask app with required ip address

```powershell
flask --app shelfmaster run -h 0.0.0.0
```

or change required line here
```python
app.run(host=<put the IP adress here>)
```
