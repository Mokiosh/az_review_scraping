import csv

with open('review_ASIN.csv', "w") as f:
    fieldnames = ['ASIN']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow({'ASIN': 'B086TCHM31'})