package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"runtime"
	"strings"
)

var (
	address string
)

const htmlBody = `
<html>
	<body>
		<h1>Uptime Checker</h1>
		<form method="GET" action="/ping">
			IP Address: <input type="text" name="ip" /><br />
			<input type="submit" value="Ping!" />
		</form>
		<div>
			<p>
				%s
			</p>
		</div>
	</body>
</html>
`

func main() {
	flag.StringVar(&address, "a", ":8080", "Address to bind to")
	flag.Parse()

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, htmlBody, "")
	})

	http.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
		ip := r.FormValue("ip")

		if len(ip) > 15 {
			fmt.Fprint(w, "IP address has exceeded the maximum length")
			return
		}

		if strings.ContainsAny(ip, "!\"#%&'+,-/:;<=>?@[\\]^_`|~ ") {
			fmt.Fprint(w, "IP address contains bad characters")
			return
		}

		var cmd *exec.Cmd
		if runtime.GOOS == "windows" {
			cmd = exec.Command("cmd", "/c", "ping "+ip)
		} else {
			cmd = exec.Command("sh", "-c", "ping -c 4 "+ip)
		}
		out, err := cmd.CombinedOutput()
		if err != nil {
			fmt.Fprintf(w, "An error has occurred: %s\n", err.Error())
			w.Write(out)
			return
		}
		fmt.Fprintf(w, htmlBody, out)
	})

	fmt.Println("Listening to", address)
	log.Fatal(http.ListenAndServe(address, nil))
}
