package main

import (
	"sync"
	"fmt"
	"sync/atomic"
)


type Vault struct {
	coins atomic.Uint64
	// guard sync.Mutex
}

func AddCoins (v *Vault){
	// v.guard.Lock()
	// defer v.guard.Unlock()
	v.coins.Add(1)
}

func main() {
	a := Vault{}
	a.coins.Store(10)
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			AddCoins(&a)
			wg.Done()
		}()
	}

	wg.Wait()
	fmt.Println(a.coins.Load())
}  