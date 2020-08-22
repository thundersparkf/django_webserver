import altair as alt
import ast 
import datetime
import pandas as pd
import pytz
import psycopg2
import json
import mysql.connector
alt.renderers.enable('json')
class Database():
    def __init__(self):
        
        
        self.host='localhost'
        self.database='rasa'
        self.user='root'
        self.password='Agastya2001#'
        
    def engine(self):
        connection = None
        try:
            connection = psycopg2.connect(host='34.121.1.190',
                                                 database='rasa',
                                                 user='postgres',
                                                 password='wulroot')
            
        except Error as error:
            print("Failed to connect: {}".format(error))
            
        finally:
            return connection   

    def query(self, mySql_select_query):
        engine = self.engine()
        cursor = engine.cursor()
        cursor.execute(mySql_select_query)
        results = cursor.fetchall()
        return results 

class Metrics():
    def __init__(self):
        self.eng = Database()

    def returned_users_data(self):
        SQL = "SELECT timestamp,(COUNT(sender_id)-1) FROM public.events WHERE type_name = 'session_started' GROUP BY timestamp;"
        results = self.eng.query(SQL)
        dates=[[result[1],datetime.datetime.fromtimestamp(result[0],tz=pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%dT%H:%M:%S')] for result in results]
        df = pd.DataFrame(dates, columns = ['Count','dates'])
        return df
    def returned_users_chart(self):
        df = self.returned_users_data()
        brush = alt.selection(type='interval', encodings=['x'])
        bars = alt.Chart().mark_bar().encode(
            x='monthdate(dates):O',
            y=alt.Y('Count:Q',scale=alt.Scale(domain=[0,2])),
            opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7)),
        ).add_selection(
            brush
        )

        line = alt.Chart().mark_rule(color='firebrick').encode(
            y='mean(Count):Q',
            size=alt.SizeValue(3)
        ).transform_filter(
            brush
        )

        returned_users = alt.layer(bars, line, data=df).properties(height=300, width=500)

        return returned_users

    def users_and_queries_data(self):
        SQL = "SELECT sender_id, timestamp FROM public.events WHERE type_name = 'user';"
        results = self.eng.query(SQL)
        times=[[result[0],datetime.datetime.fromtimestamp(result[1],tz=pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%dT%H:%M:%S')] for result in results]
        df = pd.DataFrame(times, columns=['sender','Time'])
        df['Queries'] = 1
        return df

    def users_and_queries_chart(self):
        df = self.users_and_queries_data()
        brush = alt.selection(type='interval', encodings=['y'])
        color = alt.condition(brush, alt.Color('count(Queries):Q'),alt.value('gray'))
        heat = alt.Chart(df).mark_rect().encode(
                x= alt.X("hours(Time):O",title='Time'), 
                y=alt.Y("monthdate(Time):O",title='Number of queries'),
                color= color,
                tooltip=alt.Tooltip(['sum(Queries):Q',"hours(Time):O"])).properties(
                    height=350,width=700).add_selection(
                        brush)
        line=alt.Chart(df).mark_bar().encode(
                x = alt.X('sender:N'),
                y = alt.Y('count():Q', scale=alt.Scale(domain=[0,10]))).transform_filter(
                brush).properties(
                height=200,width=675)


        rule = alt.Chart(df).transform_joinaggregate(group_count='count(*)', groupby=['sender'] ).mark_rule(color='red').encode(
            y=alt.Y('mean(group_count):Q')).transform_filter(
            brush)
        red = alt.Chart(df).transform_joinaggregate(
            group_count='count(*)', groupby=['sender'] ).mark_rule(
                color='red').encode(
                    y ='mean(group_count):Q').transform_filter(
                        brush)
        heatmap = alt.vconcat(heat, line+rule+red)

        return heatmap

    def unique_users_data(self):
        SQL = "SELECT DISTINCT sender_id, MIN(timestamp) FROM public.events WHERE type_name = 'session_started' GROUP BY sender_id;"
        results = self.eng.query(SQL)
        times=[[result[0],datetime.datetime.fromtimestamp(result[1],tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S')] for result in results]
        unique = pd.DataFrame(times, columns=['sender','time'])

        return unique
    def unique_users_chart(self):
        unique = self.unique_users_data()
        unique = alt.Chart(unique).mark_line().encode(
                    x='monthdate(time):O',
                    y='count():Q').properties(height=300, width=500)

        return unique
    def save_charts(self, chart, name):
        chart.save(name)
    
    def pipeline(self):
        metrics = [self.unique_users_chart, self.returned_users_chart, self.users_and_queries_chart]
        names = ['chart_u', 'chart_r', 'chart_q']
        charts = {}
        for metric, name in zip(metrics, names):
            chart = metric()
            charts[name] = chart.to_json()
           
            
        return dict(charts)
