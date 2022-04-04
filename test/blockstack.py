# sudo npm install -g "https://github.com/blockstack/cli-blockstack#feature/stacks-2.0-tx"

from pathlib import Path
import os
import subprocess
import json
from types import SimpleNamespace
import requests

FILE = Path('cli_keychain.json').resolve() # Path( Path.cwd(), 'cli_keychain.json')
print(FILE)
if not os.path.isdir(str(FILE)):
    subprocess.run(["blockstack", "make_keychain", "-t", ">", "cli_keychain.json"])

cli_keychain = SimpleNamespace(json.load(FILE))
print(cli_keychain)

stx_address = cli_keychain.keyInfo['address']
stx_private = cli_keychain.keyInfo['privateKey']

req_data = {'address':stx_address}
STX = requests("https://sidecar.staging.blockstack.xyz/sidecar/v1/faucets/stx",data=req_data)

process = subprocess.Popen(["blockstack", "balance", "-t", stx_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = process.communicate()
wallet = SimpleNamespace(out)
balance = wallet.balance
nonce = wallet.nonce

process = subprocess.Popen(["blockstack", "deploy_contract", "-t", "./counter.clar", "counter", "2000", balance, stx_private], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = process.communicate()

nonce_plus1 = nonce + 1
blah = subprocess.Popen(["blockstack", "call_read_only_contract_func", "-t", stx_address, "counter", "increment", "2000", nonce_plus1, key_private], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(blah)