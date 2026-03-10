package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

type ImperialTaxCollector struct {
	bucket_size  int
	bucket_times []int
	bucket_count[]int
}

func constructor(bucket_size int) ImperialTaxCollector {
	return ImperialTaxCollector{
		bucket_size:  bucket_size,
		bucket_times: make([]int, bucket_size),
		bucket_count: make([]int, bucket_size),
	}
}

func collect_tax(obj *ImperialTaxCollector) {
	cur_time := int(time.Now().Unix())
	idx := cur_time % obj.bucket_size

	if obj.bucket_times[idx] != cur_time {
		obj.bucket_times[idx] = cur_time
		obj.bucket_count[idx] = 0
	}

	obj.bucket_count[idx]++
}

func total_count(obj *ImperialTaxCollector) uint64 {
	total := 0
	cur_time := int(time.Now().Unix())
	for i := 0; i < obj.bucket_size; i++ {
		if cur_time-obj.bucket_times[i] < obj.bucket_size {
			total += obj.bucket_count[i]
		}
	}
	return uint64(total)
}
   
func main() {
	taxCollector := constructor(60)
	var expectedOps atomic.Uint64 // Used strictly to track expected count for the test
	var wg sync.WaitGroup

	numScribes := 100
	duration := 2 * time.Second

	fmt.Println("Running Unoptimized Stress Test for 2 seconds...")
	start := time.Now()

	for i := 0; i < numScribes; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for time.Since(start) < duration {
				collect_tax(&taxCollector)
				expectedOps.Add(1)
			}
		}()
	}

	wg.Wait()

	actual := total_count(&taxCollector)
	expected := expectedOps.Load()

	fmt.Printf("--------------------------------------------------\n")
	fmt.Printf("Expected Total: %d\n", expected)
	fmt.Printf("Actual Total:   %d\n", actual)
	fmt.Printf("Lost Counts:    %d\n", expected-actual)
	fmt.Printf("--------------------------------------------------\n")
}