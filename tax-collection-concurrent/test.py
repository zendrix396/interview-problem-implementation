import time
class Treasury:
    def __init__(self, bucket_size):
        self.bucket_size = bucket_size
        self.bucket_count = [0]*self.bucket_size
        self.bucket_times = [0]*self.bucket_size
    def collect_tax(self):
        curr_time = int(time.time())
        idx = curr_time % self.bucket_size
        last_updated_time = self.bucket_times[idx]
        if last_updated_time!=curr_time: 
            self.bucket_count[idx] = 0
            self.bucket_times[idx] = curr_time
        self.bucket_count[idx]+=1
    def total_tax(self):
        total = 0
        for i in range(self.bucket_size):
            total+=self.bucket_count[i]
        return total

obj = Treasury(60)
obj.collect_tax()
obj.collect_tax()
obj.collect_tax()
time.sleep(3)
obj.collect_tax()
obj.collect_tax()
time.sleep(60)
obj.collect_tax()
print(obj.total_tax())
print(obj.bucket_count)
