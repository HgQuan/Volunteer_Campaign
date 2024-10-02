import paypalrestsdk
import logging

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox hoặc live cho môi trường production
    "client_id": "AU2F14M5fgAunODLfDultP3_fh5B2b0dXjFtKafC_xU0WPxqZnyZSx7VVN-RFcVeq6j8pyRdvAwd1UJV",
    "client_secret": "EIl_7Sy_AoyBdBuYPNNn8x7_fCa6csfddkokUIuKvcfPu5sbZZqJcz6k_v366Bk2h6HRmx-63vjcuc_W"
})

logging.basicConfig(level=logging.INFO)
