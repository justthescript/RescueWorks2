# Seeding Foster Profiles for Testing

This guide explains how to seed the database with sample foster profiles for testing the foster matching features.

## Running the Seed Script

To add sample foster profiles to your database:

```bash
cd backend
python seed_fosters.py
```

## What Gets Created

The seed script creates **5 sample foster users** with the following profiles:

### 1. Sarah Johnson (sarah.foster@example.com)
- **Experience**: Advanced
- **Preferences**: Dogs and cats, all ages
- **Capacity**: 3 animals
- **Special**: Can handle medical and behavioral issues
- **Home**: House with yard, has other pets and children
- **Track Record**: 15 total fosters, 13 successful adoptions, 4.8★ rating

### 2. Mike Anderson (mike.foster@example.com)
- **Experience**: Intermediate
- **Preferences**: Dogs, adults and seniors
- **Capacity**: 2 animals
- **Special**: Can handle behavioral issues only
- **Home**: Apartment without yard, no other pets or children
- **Track Record**: 8 total fosters, 7 successful adoptions, 4.5★ rating

### 3. Emma Davis (emma.foster@example.com)
- **Experience**: Advanced
- **Preferences**: Cats, kittens and adults
- **Capacity**: 4 animals
- **Special**: Can handle medical and behavioral issues
- **Home**: House with yard, has 3 other cats
- **Track Record**: 22 total fosters, 20 successful adoptions, 5.0★ rating

### 4. James Wilson (james.foster@example.com)
- **Experience**: Beginner
- **Preferences**: Dogs and cats, adults only
- **Capacity**: 1 animal
- **Special**: No special handling capabilities
- **Home**: Condo without yard, no other pets or children
- **Track Record**: 3 total fosters, 2 successful adoptions, 4.2★ rating

### 5. Lisa Martinez (lisa.foster@example.com)
- **Experience**: Intermediate
- **Preferences**: Dogs, cats, and rabbits, young animals
- **Capacity**: 2 animals
- **Special**: Can handle medical issues
- **Home**: House with yard, has other pets and children
- **Track Record**: 11 total fosters, 10 successful adoptions, 4.6★ rating

## Login Credentials

All sample foster accounts use the same password: **password123**

Example:
- Email: `sarah.foster@example.com`
- Password: `password123`

## Testing the Matching Algorithm

Once the foster profiles are seeded, you can:

1. Navigate to the **Foster Coordinator** dashboard
2. Go to the **Foster Profiles** page to view all profiles
3. Create or update pets that need fostering
4. Use the matching algorithm to see suggested foster matches
5. Test the foster assignment workflow

## Notes

- The seed script checks for existing users before creating new ones
- All foster profiles have approved background checks and verified references
- The profiles are designed to test different matching scenarios (experience levels, preferences, capacities, etc.)
