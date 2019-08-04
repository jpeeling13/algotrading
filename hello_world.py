from __future__ import (absolute_import, division, print_function, unicode_literals);
import datetime # For datetime objects
import os.path # To manage paths
import sys # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

# Create our first test strategy!!
class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        # Logging function for this TestStrategy
        dt = dt or self.datas[0].datetime.date(0);
        print('%s, %s' % (dt.isoformat(), txt));

    def __init__(self):

        # Create a simple moving average for fun
        self.sma = bt.indicators.MovingAverageSimple(self.datas[0].close, period=10);
        # Keep a reference to the "close" line in the data[0] dataseries
        self.datasclose = self.datas[0].close;

        # To keep track of pending orders ane buy price/commission
        self.order = None;
        self.buyprice = None;
        self.buycomm = None;

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough setcash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f" % (order.executed.price, order.executed.value, order.executed.comm));
                self.buyprice = order.executed.price;
                self.buycomm = order.executed.comm;

            elif order.issell():
                self.log("SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f" % (order.executed.price, order.executed.value, order.executed.comm));
                self.buyprice = order.executed.price;
                self.buycomm = order.executed.comm;

            self.bar_executed = len(self);

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected");

        # Write down: no pending offer
        self.order = None;

    def notify_trade(self, trade):
        if not trade.isclosed:
            return;

        self.log("OPERATIONAL PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm));

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log("Close, %.2f" % self.datasclose[0]);

        # Check if an order is pending... if yes, we annot send a 2nd one
        if self.order:
            return;

        # Check if we are in the market
        if not self.position:

            # Not yet... we MIGHT BUY if ...
            if self.datasclose[0] < self.datasclose[-1]:
                # current close is less than previous Close
                if self.datasclose[-1] < self.datasclose[-2]:
                    # previous close is less than the previous close before that
                    # BUY! (with all possible default parameters)
                    self.log("BUY CREATE, %.2f" % self.datasclose[0]);
                    self.buy();

        else:
            # Already in the market... we might SELL
            if len(self) >= (self.bar_executed + 5):
                # SELL! (with all possible default parameters)
                self.log("SELL CREATE, %.2f" % self.datasclose[0]);

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell();

if __name__ == '__main__':
    # Create Cerebro entity
    cerebro = bt.Cerebro();

    # Add Strategy
    cerebro.addstrategy(TestStrategy);

    # Create a Data Feed
    data = bt.feeds.YahooFinanceData(
        dataname = "ORCL",
        # Do not pass values before this date
        fromdate = datetime.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate = datetime.datetime(2000, 6, 30),
        reverse = False
    );

    # Add the Data Feed to Cerebro
    cerebro.adddata(data);

    # Set our desired cash start
    cerebro.broker.setcash(100000.00);
    cerebro.broker.setcommission(commission=0.00);

    print("Starting Portfolio: %.2f" % cerebro.broker.getvalue())

    cerebro.run();

    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue());

    cerebro.plot();
