from __future__ import (absolute_import, division, print_function, unicode_literals);
import datetime # For datetime objects
import os.path # To manage paths
import sys # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

# Create our first test strategy!!
class TestStrategy(bt.Strategy):

    def __init__(self):
        print("Creating SMA40, SMA100, and CROSS for each Datafeed");
        self.myInds = dict();

        for datafeed in self.datas:
            self.myInds[datafeed] = dict();
            self.myInds[datafeed]["sma40"] = bt.indicators.SimpleMovingAverage(datafeed.close, period = 40);
            self.myInds[datafeed]["sma100"] = bt.indicators.SimpleMovingAverage(datafeed.close, period = 100);
            self.myInds[datafeed]["cross"] = bt.indicators.CrossOver(self.myInds[datafeed]["sma40"], self.myInds[datafeed]["sma100"]);

    def notify_order(self, order):
        pass

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isclosed:
            print('{} {} Closed: PnL Gross {}, Net {}'.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))

    def next(self):
        print(self.data.datetime.date(0));
        for datafeed in self.datas:

            # Only have 1 position at a time for each stock
            currentPosition = self.getposition(datafeed);
            if not currentPosition:

                # If the 40 SMA crossed over the 100 SMA then GO LONG!!
                if self.myInds[datafeed]["cross"][0] == 1:
                    print(datafeed._name + " - The sma40 just crossed the sma100 - BUY!!!!");
                    print(datafeed._name + " - The 40 is now: ", self.myInds[datafeed]["sma40"][0]);
                    print(datafeed._name + " - The 100 is now: ", self.myInds[datafeed]["sma100"][0]);
                    self.buy(datafeed, size = 10);

                # If the 100 SMA crossed over the 40 SMA then GO SHORT!!
                elif self.myInds[datafeed]["cross"][0] == -1:
                    print(datafeed._name + " - The sma100 just crossed the sma40 - SHORT!!!!");
                    print(datafeed._name + " - The 40 is now: ", self.myInds[datafeed]["sma40"][0]);
                    print(datafeed._name + " - The 100 is now: ", self.myInds[datafeed]["sma100"][0]);
                    self.sell(datafeed, size = 10);
            else:
                # If the 40 SMA crossed over the 100 SMA then CLOSE OUT YOUR SHORT AND GO LONG!!
                if self.myInds[datafeed]["cross"][0] == -1:
                    print(datafeed._name + " - The sma100 just crossed the sma40 - CLOSE SHORT AND GO LONG!!!!");
                    print(datafeed._name + " - The 40 is now: ", self.myInds[datafeed]["sma40"][0]);
                    print(datafeed._name + " - The 100 is now: ", self.myInds[datafeed]["sma100"][0]);
                    self.close(datafeed);
                    self.buy(datafeed, size = 10)

                # If the 100 SMA crossed over the 40 SMA then CLOSE OUT YOUR LONG AND GO SHORT!!
                if self.myInds[datafeed]["cross"][0] == -1:
                    print(datafeed._name + " - The sma100 just crossed the sma40 - CLOSE LONG AND GO SHORT!!!!");
                    print(datafeed._name + " - The 40 is now: ", self.myInds[datafeed]["sma40"][0]);
                    print(datafeed._name + " - The 100 is now: ", self.myInds[datafeed]["sma100"][0]);
                    self.close(datafeed);
                    self.sell(datafeed, size = 10);

if __name__ == '__main__':
    # Create Cerebro entity
    cerebro = bt.Cerebro();

    # Add Strategy
    cerebro.addstrategy(TestStrategy);

    # Create a Data Feed
    data1 = bt.feeds.YahooFinanceData(
        dataname = "ORCL",
        # Do not pass values before this date
        fromdate = datetime.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate = datetime.datetime(2005, 6, 30),
        reverse = False
    );

    data2 = bt.feeds.YahooFinanceData(
        dataname = "AAPL",
        # Do not pass values before this date
        fromdate = datetime.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate = datetime.datetime(2005, 6, 30),
        reverse = False
    );
    # Add the Data Feed to Cerebro
    cerebro.adddata(data1, "Oracle Stock");
    cerebro.adddata(data2, "Apple Stock");

    # Set our desired cash start
    cerebro.broker.setcash(100000.00);
    cerebro.broker.setcommission(commission=0.00);

    print("Starting Portfolio: %.2f" % cerebro.broker.getvalue())

    cerebro.run();

    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue());

    cerebro.plot();
