# Check what's available in pqcrypto
try:
    import pqcrypto
    print("pqcrypto imported successfully")
    print("pqcrypto location:", pqcrypto.__file__)
    
    import pqcrypto.sign
    print("\nSign module contents:")
    print(dir(pqcrypto.sign))
    
    import pqcrypto.kem
    print("\nKEM module contents:")
    print(dir(pqcrypto.kem))
    
    # Try to see what's actually in the sign module
    import os
    sign_path = os.path.join(os.path.dirname(pqcrypto.__file__), 'sign')
    if os.path.exists(sign_path):
        print("\nSign directory contents:")
        print(os.listdir(sign_path))
    
    kem_path = os.path.join(os.path.dirname(pqcrypto.__file__), 'kem')
    if os.path.exists(kem_path):
        print("\nKEM directory contents:")
        print(os.listdir(kem_path))
        
except Exception as e:
    print("Error:", e)