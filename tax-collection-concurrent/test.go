package main

import (
	"sync"
	"sync/atomic"
	"fmt"
	"time"
)

type taxCollector struct {
	bucket_size uint64
	bucket_count []atomic.Uint64
	bucket_times []atomic.Uint64
	bucket_locks []sync.Mutex
}

func Constructor(size int) *taxCollector {
	return &taxCollector{
		bucket_size: uint64(size),
		bucket_count: make([]atomic.Uint64, size),
		bucket_times: make([]atomic.Uint64, size),
		bucket_locks: make([]sync.Mutex, size),
	}
}

func collectTax(obj *taxCollector){
	cur_time := uint64(time.Now().Unix())
	idx := int(cur_time%obj.bucket_size)
	last_updated_time := obj.bucket_times[idx].Load()
	if last_updated_time != cur_time {
		obj.bucket_locks[idx].Lock()
		if obj.bucket_times[idx].Load() != cur_time{
			obj.bucket_count[idx].Store(0)
			obj.bucket_times[idx].Store(cur_time)
		}
		obj.bucket_locks[idx].Unlock()
	}
	obj.bucket_count[idx].Add(1)
}

func totalTax(obj *taxCollector) int{
	totalCoins := 0
	cur_time:= uint64(time.Now().Unix())
	for i:=0; i<int(obj.bucket_size);i++{
		if cur_time - obj.bucket_size <= obj.bucket_times[i].Load(){
			totalCoins+=int(obj.bucket_count[i].Load())
		}
	}
	return totalCoins
}
func main (){
	treasury := Constructor(60)
	var wg sync.WaitGroup
	for i:=0; i<10000000; i++ {
		wg.Add(1)
		go func () {
			defer wg.Done()
			collectTax(treasury)
		}()
	}
	wg.Wait()
	fmt.Println("Total Tax: ", totalTax(treasury))
	fmt.Println("All taxes collected safely.")
}
