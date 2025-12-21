INSERT INTO githappens_users.users (
    username, 
    email, 
    password_hash, 
    dob, 
    gender, 
    is_admin, 
    score
) VALUES (
    'admin_canavari', 
    'admin@example.com', 
    'scrypt:32768:8:1$tHD9cn4gyZWUVnLP$0b37dda62b17004b9833264ba932e87e09ed6de5a533422ee3dfecc0f5741e467b3796d0014b24ed7e0a65a0a4844bbb2981b9eef46e963e9e49bcbadc0830fa', 
    '1990-01-01', 
    'Male', 
    1, -- is_admin: 1 (Admin yetkisi verildi)
    0
);


SET SQL_SAFE_UPDATES = 0; -- Korumayı kapat

UPDATE users
SET is_admin = 1
WHERE username = 'adminfaruk';

SET SQL_SAFE_UPDATES = 1; -- Korumayı tekrar aç