import csv
class CsvHelper:
    def write(self, filename, arrRows):
        with open(filename, mode='w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in arrRows:
                csv_writer.writerow(row)
           
def main():
    csv = CsvHelper()
    arr = [["a","b"],["c","d"]]
    csv.write("test.csv", arr)

if __name__ == "__main__":
    # call main function
    main()