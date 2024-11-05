import winreg
import ctypes
import argparse

def getRegKeyClassName(subkey, hkey, verbose):
    if verbose:
        print(f"Opening Registry Key: {subkey}...")

    try:
        key = winreg.OpenKeyEx(hkey, subkey, 0, winreg.KEY_ALL_ACCESS)
        if verbose:
            print(f"Successfully Opened Key: {subkey}")
    except Exception as e:
        print(f"Error opening Key {subkey}. Error: {e}")

    key_handle = key.handle


    if verbose:
        print(f"Getting Class Name of Registry Key {subkey}")

    # Prepare to call RegQueryInfoKeyW
    class_name_buffer = ctypes.create_unicode_buffer(256)  # Buffer for the class name
    class_name_size = ctypes.c_ulong(ctypes.sizeof(class_name_buffer) // ctypes.sizeof(ctypes.c_wchar))

    subkey_count = ctypes.c_ulong()
    value_count = ctypes.c_ulong()
    max_subkey_len = ctypes.c_ulong()
    max_value_len = ctypes.c_ulong()
    security_descriptor_size = ctypes.c_ulong()
    last_write_time = ctypes.c_ulong()  # Not used but needs to be present

    result = ctypes.windll.advapi32.RegQueryInfoKeyW(
        key_handle,
        class_name_buffer,
        ctypes.byref(class_name_size),
        None,
        ctypes.byref(subkey_count),
        ctypes.byref(max_subkey_len),
        None,
        ctypes.byref(value_count),
        ctypes.byref(max_value_len),
        None,
        ctypes.byref(security_descriptor_size),
        ctypes.byref(last_write_time)
    )

    if result == 0:  # ERROR_SUCCESS
        class_name = class_name_buffer.value if class_name_buffer.value else "<NO CLASS>"
        if verbose:
            print(f"Successfully Retrieved Class Name for Registry Key {subkey}: {class_name}\n")
        return class_name
    else:
        print(f"Error querying registry key info. Code: {result}")

    winreg.CloseKey(key)

def main(verbose, output_file):

    JDKeyPath = r"SYSTEM\CurrentControlSet\Control\Lsa\JD"
    Skew1KeyPath = r"SYSTEM\CurrentControlSet\Control\Lsa\Skew1"
    GBGKeyPath = r"SYSTEM\CurrentControlSet\Control\Lsa\GBG"
    DataKeyPath = r"SYSTEM\CurrentControlSet\Control\Lsa\Data"

    JDClassName = getRegKeyClassName(JDKeyPath, winreg.HKEY_LOCAL_MACHINE, verbose)

    Skew1ClassName = getRegKeyClassName(Skew1KeyPath, winreg.HKEY_LOCAL_MACHINE, verbose)
    GBGClassName = getRegKeyClassName(GBGKeyPath, winreg.HKEY_LOCAL_MACHINE, verbose)
    DataClassName = getRegKeyClassName(DataKeyPath, winreg.HKEY_LOCAL_MACHINE, verbose)

    if verbose:
        print("Calculating LSA Key...\n")

    LSAKey = JDClassName + Skew1ClassName + GBGClassName + DataClassName

    if output_file:
        print(f"Writing LSA Key to {output_file}.")
        with open(output_file, 'w') as file:
            file.write(LSAKey)
    else:
        print(f"LSA Key = {LSAKey}")

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="A security tool that retrieves the Windows LSA Key from the Registry.")

    # Add arguments
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode.")
    parser.add_argument("-o", "--output", type=str, help="Output to a specified file.")

    # Parse the command line arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(args.verbose, args.output)
