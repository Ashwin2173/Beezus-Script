package main

import (
    "os"
    "fmt"
    "bufio"
    "strconv"
)

func main() { main__() }

func print(message ...any) {
    fmt.Println(message...)
}

func input(message ...any) string {
    fmt.Print(message...)
    input, _ := bufio.NewReader(os.Stdin).ReadString('\n')
    return input[:len(input)-1]
}

func int(value any) int64 {
    switch v := value.(type) {
    case int8:
        return int64(v)
    case int16:
        return int64(v)
    case int32:
        return int64(v)
    case int64:
        return v
    case uint:
        return int64(v)
    case uint8:
        return int64(v)
    case uint16:
        return int64(v)
    case uint32:
        return int64(v)
    case uint64:
        return int64(v)
    case float32:
        return int64(v)
    case float64:
        return int64(v)
    case string:
        if i, err := strconv.ParseInt(v, 10, 64); err == nil {
            return i
        }
        if f, err := strconv.ParseFloat(v, 64); err == nil {
            return int64(f)
        }
    }

    panic(fmt.Sprintf("int() can convert string or float to int, but not %T", value))
}
