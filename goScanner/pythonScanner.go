package main

import (
	"fmt"
	"net"
	"C"
	"sync"
	)
//export fastScanner
func fastScanner(){

	ip :="127.0.0.1"
	ports := 4000
	var wg sync.WaitGroup
	for i:=1;i<=ports;i++{
		wg.Add(1)		
		go func(j int){
			defer wg.Done()
			address := fmt.Sprintf("%s:%d",ip,j)
			conn,err:= net.Dial("tcp",address)
			if err == nil{
				fmt.Println("Port open: ",j)
				conn.Close()			
}
			
		}(i)
	}
	wg.Wait()
}
			

func main(){

}