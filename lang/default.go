package main
import "fmt"
func main() { main__() }
func print(message ...any) {
for _, item := range message {
fmt.Print(item, " ")
}
}