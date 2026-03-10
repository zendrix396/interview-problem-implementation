# tax collector
## 4 key parts
* main backend: circular buffer round table
* wrapping to get rest api => testing benchmark using wrk/jmeter 
* redisfy it => several request updating single redis memory window
* ui dashboard => hyperloglog as well polling script and other optimization

---
> different de-centralized nodes => nginx and other scaling techniques


**tech stack**: go/python, fastapi, redis, nginx