# ERC20 Example

The `py-patract` is based on python3, so need install at first:

```bash
sudo apt-get install python3 python3-pip
```

Then install `patract-interface` by pip:

```bash
pip3 install -U patract-interface 
```

Note the `patract-interface` version is `v0.3.1`:

```bash
pip3 list | grep patract-interface
patract-interface      0.3.1
```

Clone the `py-patract`:

```bash
git clone https://github.com/patractlabs/py-patract.git
cd ./py-patract
```

Start `europa` for test env:

```bash
europa --tmp --dev
```

Run examples:

```bash
python3 ./examples/erc20/erc20.py 
```

If success will show:

```bash
python3 ./examples/erc20/erc20.py 
transfer res True
on_transfer in 1 : None 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY 1000000000000000000000
on_transfer in 2 : 5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY 5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty 100000
```
