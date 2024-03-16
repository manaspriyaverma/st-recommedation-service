import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def change_label_style(label, font_size='12px', font_color='black', font_family='sans-serif'):
    html = f"""
    <script>
        var elems = window.parent.document.querySelectorAll('p');
        var elem = Array.from(elems).find(x => x.innerText == '{label}');
        elem.style.fontSize = '{font_size}';
        elem.style.color = '{font_color}';
        elem.style.fontFamily = '{font_family}';
    </script>
    """

header = r'''
$\textsf{
    \Large Optimizing Airfare Strategies: Discount Opportunity Scouting
}$
'''

st.write(header)

data = pd.read_csv("recommendation.csv")
inputdata = pd.read_csv("data.csv")
airlinelist = data['platng_carrier_key'].unique()

airline = st.selectbox("Select Airline", airlinelist)

routelist = data[data['platng_carrier_key'] == airline]['tckt_route_key'].unique()
route = st.selectbox("Select Routes", routelist)

traveldatelist = data[(data['platng_carrier_key'] == airline) & (data['tckt_route_key'] == route)]['travel_date'].unique()
traveldate = st.selectbox("Select Travel Date", traveldatelist)

value = st.button('Run Simulation')

if value:

	true_data = inputdata[(inputdata['platng_carrier_key'] == airline) & (inputdata['tckt_route_key'] == route) & (inputdata['travel_date'] == traveldate)]
	recommeded_data = data[(data['platng_carrier_key'] == airline) & (data['tckt_route_key'] == route) & (data['travel_date'] == traveldate)]

	simulated_data = true_data.copy()
	simulated_data['price'] = simulated_data.apply(lambda x: x['price']*(1-recommeded_data['discount'][0]) if x['bk_windw_cat'] == recommeded_data['bk_windw_cat'][0] else x['price'], axis = 1)
	simulated_data['bookings'] = simulated_data.apply(lambda x: x['bookings'] + recommeded_data['incremental_bookings'][0] if x['bk_windw_cat'] == recommeded_data['bk_windw_cat'][0] else x['bookings'], axis = 1)
	simulated_data['type'] = 'Recommeded'

	true_data['type'] = 'Actual'

	st.write("**Recommendation: " + 
		"Offering discount of " + 
		str(int(recommeded_data['discount'][0]*100)) + "%" + 
		" on booking window of " + str(recommeded_data['bk_windw_cat'][0]) + 
		" will lead to incremental bookings of " + str(int(recommeded_data['incremental_bookings'][0])) + "**")


	st.write('Showing Price/Bookings Plots')


	df1 = true_data[['type', 'bk_windw_cat', 'price', 'bookings']]
	df2 = simulated_data[['type', 'bk_windw_cat', 'price', 'bookings']]
	df3 = pd.concat([df1, df2]).sort_values(by = "type", ascending = False)

	fig, axes = plt.subplots(2, 1, figsize=(15, 15))

	sns.lineplot(data=df3[['type', 'bk_windw_cat', 'price']], x = "bk_windw_cat", y= "price", hue = "type", style="type", ax = axes[0])
	sns.lineplot(data=df3[['type', 'bk_windw_cat', 'bookings']], x = "bk_windw_cat", y= "bookings", hue = "type", style="type", ax = axes[1])
	st.pyplot(fig.get_figure())
