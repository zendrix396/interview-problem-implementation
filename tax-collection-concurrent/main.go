package main

import (
	"fmt"
	"sync/atomic"
	"time"
	"math/rand/v2"
	"sync"
)
type ImperialTaxCollector struct {
    bucket_size int;
    bucket_times []atomic.Uint64;
    bucket_count []atomic.Uint64;
	// lock per bucket
	// bucket_locks []sync.Mutex;
}
func constructor(bucket_size int) ImperialTaxCollector {
    return ImperialTaxCollector{
        bucket_size: bucket_size,
        bucket_times: make([]atomic.Uint64, bucket_size),
        bucket_count: make([]atomic.Uint64, bucket_size),
		// bucket_locks: make([]sync.Mutex, bucket_size),
    }
}
func collect_tax(obj *ImperialTaxCollector) {
	cur_time := int(time.Now().Unix());
	idx := int64(cur_time%obj.bucket_size);
	// last_touch := obj.bucket_times[idx].Load()
	// if int(last_touch) != cur_time{
		// lock that shit
		// obj.bucket_locks[idx].Lock()
		// second verification
		if int(obj.bucket_times[idx].Load()) != cur_time {
			// t1 and t2 goes there
			obj.bucket_times[idx].Store(uint64(cur_time));
			// mutex goes there 
			obj.bucket_count[idx].Store(0);
		}

		// obj.bucket_locks[idx].Unlock()
	// }
	obj.bucket_count[idx].Add(1);
	fmt.Println("total count increase", obj.bucket_count[idx].Load())
} 
func total_count(obj *ImperialTaxCollector) uint64{
	var total atomic.Uint64
	cur_time := int(time.Now().Unix());
	for i:=0;i<obj.bucket_size;i++ {
		if uint64(cur_time)-obj.bucket_times[i].Load()<uint64(obj.bucket_size){
			total.Add(obj.bucket_count[i].Load());
		}
	}
	return total.Load()
}
func randRange(min, max int) int {
	return rand.IntN(max-min+1) + min
}
func main(){
	a := constructor(60);
	x := 4
	y := 1
	items := make([]string, 0, x+y);
	for i:=0;i<x;i++ {
		items = append(items, "collect_tax")
	}
	for i:=0;i<y;i++ {
		items = append(items, "total_count")
	}
	var wg sync.WaitGroup 
	for i:=0;i<100000;i++{
		wg.Add(1)
		go func(){
			// reqInt := randRange(0,x+y-1)
			// if items[reqInt] == "collect_tax" {
			collect_tax(&a)
			// } else {
			// 	fmt.Println("total:",total_count(&a));
			// }
			wg.Done()
		}()
	}
	wg.Wait()
	fmt.Println("total:",total_count(&a))
}
