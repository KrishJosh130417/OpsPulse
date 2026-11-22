import os
import json
import urllib.request
from pathlib import Path
from datetime import date, datetime, timedelta
import random
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title='OpsPulse | Fulfillment Control Tower', page_icon='📦', layout='wide')
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
ORDERS_FILE = DATA_DIR / 'orders.csv'
INVENTORY_FILE = DATA_DIR / 'inventory.csv'
ORDER_COLUMNS = ['order_id','order_date','hub','product','quantity','status','promised_minutes','actual_minutes','unit_price']
INVENTORY_COLUMNS = ['hub','product','opening_stock','received','allocated','reorder_level']
HUBS = ['North Hub','Central Hub','South Hub']
PRODUCTS = {'Chicken Breast': 249, 'Fish Fillet': 329, 'Paneer': 179, 'Eggs (12-pack)': 99, 'Fresh Vegetables': 129}
STATUSES = ['Delivered','Dispatched','Pending','Cancelled']


def seed_data():
    if not INVENTORY_FILE.exists():
        inventory = []
        for hub in HUBS:
            for i, product in enumerate(PRODUCTS):
                opening = 150 + i * 18
                received = 30 + i * 5
                allocated = 105 + i * 17 + (30 if hub == 'North Hub' else 0)
                inventory.append([hub, product, opening, received, allocated, 45])
        pd.DataFrame(inventory, columns=INVENTORY_COLUMNS).to_csv(INVENTORY_FILE, index=False)
    if not ORDERS_FILE.exists():
        rng = random.Random(42)
        rows = []
        for i in range(180):
            hub = rng.choice(HUBS)
            product = rng.choice(list(PRODUCTS))
            status = rng.choices(STATUSES, weights=[68, 18, 11, 3])[0]
            promised = 45
            actual = rng.randint(22, 78) if status == 'Delivered' else 0
            rows.append([f'ORD-{1001+i}', (date.today()-timedelta(days=rng.randint(0,13))).isoformat(), hub, product, rng.randint(1,4), status, promised, actual, PRODUCTS[product]])
        pd.DataFrame(rows, columns=ORDER_COLUMNS).to_csv(ORDERS_FILE, index=False)


def load_orders():
    df = pd.read_csv(ORDERS_FILE)
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    for col in ['quantity','promised_minutes','actual_minutes','unit_price']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df


def load_inventory():
    df = pd.read_csv(INVENTORY_FILE)
    for col in ['opening_stock','received','allocated','reorder_level']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['available_stock'] = df['opening_stock'] + df['received'] - df['allocated']
    df['stock_alert'] = df['available_stock'] <= df['reorder_level']
    return df


def metrics(df):
    total = len(df)
    delivered = df['status'].eq('Delivered')
    dispatched = df['status'].isin(['Delivered','Dispatched'])
    completed = df[delivered]
    on_time = (completed['actual_minutes'] <= completed['promised_minutes']).sum()
    return {
        'orders': total,
        'dispatched': int(dispatched.sum()),
        'dispatch_rate': 100 * dispatched.sum()/total if total else 0,
        'pending': int(df['status'].eq('Pending').sum()),
        'on_time_rate': 100 * on_time / len(completed) if len(completed) else 0,
        'revenue': float((completed['quantity'] * completed['unit_price']).sum()),
    }


def send_webhook(payload, url):
    request = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.status


seed_data()
orders = load_orders()
inventory = load_inventory()
st.title('📦 OpsPulse')
st.caption('Fulfillment Operations Control Tower · Demonstration dataset')

with st.sidebar:
    st.header('Operations Center')
    page = st.radio('Navigation', ['Dashboard','Orders & Data Entry','Inventory','Reports & Automation'])
    hub_filter = st.selectbox('Hub', ['All hubs'] + HUBS)
    min_day = orders['order_date'].min().date()
    max_day = max(date.today(), orders['order_date'].max().date())
    dates = st.date_input('Order date range', value=(min_day, max_day), min_value=min_day, max_value=max_day)
    st.caption('All figures use fictional demonstration data. Changes are saved locally to CSV.')

filtered = orders.copy()
if hub_filter != 'All hubs':
    filtered = filtered[filtered['hub'] == hub_filter]
if isinstance(dates, (tuple,list)) and len(dates) == 2:
    filtered = filtered[filtered['order_date'].dt.date.between(dates[0], dates[1])]
selected_inventory = inventory if hub_filter == 'All hubs' else inventory[inventory['hub'] == hub_filter]
m = metrics(filtered)

if page == 'Dashboard':
    st.subheader('Operations Overview')
    a,b,c,d = st.columns(4)
    a.metric('Total Orders', f"{m['orders']:,}")
    b.metric('Dispatched / Delivered', f"{m['dispatched']:,}", f"{m['dispatch_rate']:.1f}% dispatch rate")
    c.metric('Pending Orders', f"{m['pending']:,}")
    d.metric('On-Time Delivery', f"{m['on_time_rate']:.1f}%")
    e,f = st.columns(2)
    e.metric('Delivered Order Value', f"₹{m['revenue']:,.0f}")
    f.metric('Low-Stock / Stockout Alerts', int(selected_inventory['stock_alert'].sum()))
    st.divider()
    left,right = st.columns(2)
    with left:
        st.markdown('#### Orders by Day')
        daily = filtered.groupby(filtered['order_date'].dt.date).size().rename('Orders')
        st.bar_chart(daily)
    with right:
        st.markdown('#### Order Status Mix')
        status_counts = filtered['status'].value_counts().rename('Orders')
        st.bar_chart(status_counts)
    st.markdown('#### Exceptions Requiring Attention')
    delayed = filtered[(filtered['status'] == 'Delivered') & (filtered['actual_minutes'] > filtered['promised_minutes'])]
    st.write(f'Late deliveries: **{len(delayed)}** | Pending orders: **{m["pending"]}** | Low-stock lines: **{int(selected_inventory["stock_alert"].sum())}**')
    if len(delayed):
        st.dataframe(delayed[['order_id','order_date','hub','product','promised_minutes','actual_minutes']].head(12), use_container_width=True, hide_index=True)

elif page == 'Orders & Data Entry':
    st.subheader('Record an Order')
    with st.form('new_order', clear_on_submit=True):
        x,y,z = st.columns(3)
        order_id = x.text_input('Order ID', value=f"ORD-{int(datetime.now().timestamp())}")
        order_date = y.date_input('Order Date', value=date.today())
        hub = z.selectbox('Fulfillment Hub', HUBS)
        x,y,z = st.columns(3)
        product = x.selectbox('Product', list(PRODUCTS))
        qty = y.number_input('Quantity', min_value=1, max_value=100, value=1)
        status = z.selectbox('Status', STATUSES)
        x,y = st.columns(2)
        promised = x.number_input('Promised Minutes', min_value=1, value=45)
        actual = y.number_input('Actual Minutes (0 if not delivered)', min_value=0, value=0)
        submitted = st.form_submit_button('Save Order', type='primary')
        if submitted:
            existing_ids = set(orders['order_id'].astype(str))
            if not order_id.strip():
                st.error('Order ID cannot be blank.')
            elif order_id.strip() in existing_ids:
                st.error('This Order ID already exists.')
            elif status == 'Delivered' and actual == 0:
                st.error('Delivered orders must have an actual delivery time greater than zero.')
            else:
                row = pd.DataFrame([[order_id.strip(), order_date.isoformat(), hub, product, int(qty), status, int(promised), int(actual), PRODUCTS[product]]], columns=ORDER_COLUMNS)
                row.to_csv(ORDERS_FILE, mode='a', header=False, index=False)
                st.success('Order saved. Refresh or rerun to update the dashboard.')
    st.markdown('#### Orders Ledger')
    st.dataframe(filtered.sort_values('order_date', ascending=False), use_container_width=True, hide_index=True)

elif page == 'Inventory':
    st.subheader('Warehouse Inventory Allocation')
    st.caption('Available stock = Opening stock + Received − Allocated')
    st.dataframe(selected_inventory, use_container_width=True, hide_index=True)
    alerts = selected_inventory[selected_inventory['stock_alert']]
    if len(alerts):
        st.warning(f'{len(alerts)} product-hub combinations are at or below reorder level.')
    else:
        st.success('No inventory alerts for the selected hub.')
    st.markdown('#### Update an Inventory Record')
    with st.form('inventory_update'):
        x,y = st.columns(2)
        hub = x.selectbox('Hub to Update', HUBS)
        product = y.selectbox('Product to Update', list(PRODUCTS))
        match = inventory[(inventory['hub']==hub) & (inventory['product']==product)].iloc[0]
        x,y,z,w = st.columns(4)
        opening = x.number_input('Opening Stock', min_value=0, value=int(match['opening_stock']))
        received = y.number_input('Received', min_value=0, value=int(match['received']))
        allocated = z.number_input('Allocated', min_value=0, value=int(match['allocated']))
        reorder = w.number_input('Reorder Level', min_value=0, value=int(match['reorder_level']))
        update = st.form_submit_button('Save Inventory', type='primary')
        if update:
            if allocated > opening + received:
                st.error('Allocated quantity cannot exceed opening stock plus received stock.')
            else:
                raw = pd.read_csv(INVENTORY_FILE)
                mask = (raw['hub']==hub) & (raw['product']==product)
                raw.loc[mask, ['opening_stock','received','allocated','reorder_level']] = [opening,received,allocated,reorder]
                raw.to_csv(INVENTORY_FILE, index=False)
                st.success('Inventory updated. Refresh or rerun to see the new balance.')

else:
    st.subheader('Reports & Automation')
    st.write('Generate a filtered operational report and optionally send its KPI summary to an n8n webhook.')
    st.markdown('#### Current Reporting Summary')
    st.json({**{k: round(v,2) if isinstance(v,float) else v for k,v in m.items()}, 'low_stock_alerts': int(selected_inventory['stock_alert'].sum()), 'hub':hub_filter})
    x,y = st.columns(2)
    x.download_button('Download Orders CSV', filtered.to_csv(index=False).encode('utf-8'), 'opspulse_orders.csv', 'text/csv')
    y.download_button('Download Inventory CSV', selected_inventory.to_csv(index=False).encode('utf-8'), 'opspulse_inventory.csv', 'text/csv')
    st.markdown('#### Email Report to Evaluator')
    st.write('Enter a recipient email and send the selected hub’s KPI summary through n8n.')
    with st.form('send_report_form'):
        evaluator_email = st.text_input(
            'Evaluator Email Address',
            placeholder='evaluator@example.com',
            help='The report will be sent to this address by your n8n Gmail workflow.'
        )
        webhook = st.text_input(
            'n8n Webhook URL',
            value=os.environ.get('OPSPULSE_N8N_WEBHOOK', ''),
            type='password',
            help='Use the test URL while listening for a test event, or the production URL after activating your workflow.'
        )
        send_report = st.form_submit_button('Send KPI Report to Evaluator', type='primary')

    if send_report:
        recipient = evaluator_email.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
            st.error('Please enter a valid evaluator email address.')
        elif not webhook.strip().startswith('https://'):
            st.error('Enter a valid HTTPS n8n webhook URL.')
        else:
            payload = {
                'source': 'OpsPulse',
                'generated_at': datetime.now().isoformat(),
                'hub': hub_filter,
                'metrics': m,
                'low_stock_alerts': int(selected_inventory['stock_alert'].sum()),
                'recipient_email': recipient,
            }
            try:
                code = send_webhook(payload, webhook.strip())
                if 200 <= code < 300:
                    st.success(f'n8n accepted the report request (HTTP {code}). Check the n8n execution and Gmail delivery to {recipient}.')
                else:
                    st.warning(f'n8n responded with HTTP {code}. Check the workflow execution.')
            except Exception as exc:
                st.error(f'Webhook request failed: {exc}')

st.caption('OpsPulse prototype · Demo records only · CSV storage is local to this installation')
