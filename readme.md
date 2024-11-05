# LSA Hunter
A tool for extracting the LSA Key of a Windows machine from the Registry.

## Usage
Download LSA Hunter:

`git clone https://github.com/declangray/lsa-hunter`

Run the `lsahunter.py` script using python:

`python lsahunter.py`

*Note: LSA Hunter requires Python 3, so if you are having trouble try running* `python3 lsahunter.py`

**Depending on your permission level, you may need to run the script as Administrator.**

### Arguments
LSA Hunter supports some arguments:
- You can use the flag `-v` or `--verbose` for a more verbose output.
- You can use the flag `-o` or `--output` to output to a specified file.
- You can use the flag `-h` or `--help` for a help message.

## How it works
As I was scrolling through my YouTube recommendations, I came across [this video](https://www.youtube.com/watch?v=Hq_RgcYL9_k) by [Enderman](https://enderman.ch/) - a software engineer and YouTuber. The video discusses a way to obtain Windows credentials by first obtaining the LSA Key in order to decrypt LSA Secrets, and thus obtaining the hashed credentials stored within. I would highly recommend watching the full video as it goes into depth about how passwords are stored on Windows. What I found most interesting however, was the method used to obtain the LSA Key.

### What is an LSA Key
First of all, the Local Security Authority, or LSA is a service on Windows that handles security *things* - such as storing passwords and other sensitive information. The LSA Key is an encryption key which is used to encrypt and decrypt the LSA "secrets" (essentially, your passwords) - and as we all know: Windows is the *most* secure operating system in the world, so this LSA Key is safeguarded properly... right?

### oh...

The LSA Key is stored **in the Registry**... although in a very strange way. As explained in Enderman's video, the LSA Key is 16 bytes (128 bits) stored in 4 seperate keys as 4 byte chunks.

These 4 byte chunks can be found in the following keys:
- `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA\JD`
- `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA\Skew1`
- `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA\GBG`
- `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA\Data`

However, the bytes are not stored in a Key Value, instead they are stored in a hidden attribute: `Class Name`. When exporting the previously mentioned keys as a .txt (or printing them to PDF, yes seriously...), you will get the following output:

```
Key Name:          HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\JD
Class Name:        ff8cd910
Last Write Time:   19/09/2024 - 8:24 PM
Value 0
  Name:            Lookup
  Type:            REG_BINARY
  Data:            
00000000   ac 36 16 8e 7a 26                                  ¬6..z&
```

The value of `Class Name` is the 4 bytes that, when combined with the others in the correct order, make up the full LSA Key. These `Class Name` values must be combined in the following order to derive the LSA Key: JD, Skew1, GBG, Data.

So it seems that Microsoft opted for security through obscurity by hiding the LSA Key in a *basically unused* registry attribute, rather than actually securing anything. I also find it very amusing that you can print registry keys.

### LSA Hunter
I was inspired by this weird storing of such a crucial piece of information to make LSA Hunter, which simply automates the process of grabbing each byte chunk and combining them in the correct order to obtain the LSA Key. LSA Hunter uses the `winreg` and `ctypes` libraries to open each key, grab the `Class Name` and then just combines them in the correct order using string concatenation to produce the LSA Key.


