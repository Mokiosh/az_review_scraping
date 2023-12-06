import pandas as pd
import datetime


now = datetime.datetime.today()
today = now.strftime("%Y%m%d")

input_dir_path = '../input_dir'
output_dir_path = '../output_dir'
input_file = f"{today}_done_ASIN.csv"
filename = f"{today}_review_sum.csv"

columns = ["PNAME", "ASIN", "product", "brand", "name", "date", "score", "title",
           "comment"]


def get_data(csv):
    items = []
    for l in open(csv):
        items.append(l)

    num_items = len(items)
    for i, line in enumerate(open(csv)):
        progress = int(i / num_items * 100)
        print(f'Getting results...: {progress}%', end='\r')
        yield line.strip().split(",")
    print()


for i in get_data(f"{output_dir_path}/{input_file}"):
    simple_key = str(i).replace("['", "").replace("']", "")
    df_add = pd.read_csv(f"{output_dir_path}/{str(simple_key)}",
                         header=None, encoding="utf_8", names=columns,
                         skiprows=1)

    # Too many varieties to make patterns
    # if df_add.iat[0, 7] == None:
    #     df_add["comment"] = df_add["date"]
    #     df_add["title"] = df_add["name"]
    #     df_add["score"] = df_add["brand"]
    #     df_add["date"] = df_add["product"]
    #     df_add["name"] = df_add["ASIN"]
    #
    #     length = len(df_add["date"])
    #     empty_box = []
    #
    #     for j in range(length):
    #         empty_box.append("NaN")
    #     df_add["ASIN"] = empty_box
    #     df_add["product"] = empty_box
    #     df_add["brand"] = empty_box
    #
    # else:
    #     pass

    length = len(df_add["date"])
    name_box = []
    for j in range(length):
        name_box.append(simple_key)
    df_add["PNAME"] = name_box

    try:
        df = pd.read_csv(f'{output_dir_path}/{filename}',
                         header=None, encoding="utf_8", names=columns,
                         skiprows=1)

    except:
        df = pd.DataFrame(columns=columns)

    df_fin = pd.concat([df, df_add])
    df_fin.to_csv(f'{output_dir_path}/{filename}')
