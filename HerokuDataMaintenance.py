import pandas as pd
from sqlalchemy import create_engine
# you also need to install psycopg2



def write_data_to_database(local_data_path, database, engine):

    # read local data
    df = pd.read_excel(local_data_path, index_col=0)

    # write the dataframe to sql
    df.to_sql(database, con=engine, if_exists='replace', chunksize=1000)


def read_data_from_database(database, engine):
    # this is to get what data are stored in postgres db, use index_col to specify what column you want as index
    df = pd.read_sql(sql=database, con=engine, index_col='index')

    # store the dataframe into xlsx file
    df.to_excel(r'Data retrieved from database.xlsx')


if __name__ == '__main__':
    # create sqlalchemy engine with postgres database URL
    DATABASE_URL = 'postgresql://cemlwhkqzhydbc:ce0242f300bb5ca5788c806b76f1119170b10323114b25b6bbccb03630b71a27@ec2-54-74-35-87.eu-west-1.compute.amazonaws.com:5432/da06s7pv1tg2em'
    engine = create_engine(DATABASE_URL, echo=False)

    # run to update database with your local data
    write_data_to_database(local_data_path=r"C:\Users\ARIS\Desktop\official.xlsx", database='Covid-19-Cases', engine=engine)

    # run to get what the database has stored
    # read_data_from_database(database='Covid-19-Cases', engine=engine)
