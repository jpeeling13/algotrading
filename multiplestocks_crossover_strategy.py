from __future__ import (absolute_import, division, print_function, unicode_literals);
import datetime # For datetime objects
import os.path # To manage paths
import sys # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

# Create our first test strategy!!
class TestStrategy(bt.Strategy):

    params = (('sma1', 40),('sma2', 100),);

    def __init__(self):
        print("Creating sma1, sma2, and CROSS for each Datafeed");
        self.myInds = dict();

        for datafeed in self.datas:
            self.myInds[datafeed] = dict();
            self.myInds[datafeed]["sma1"] = bt.indicators.SimpleMovingAverage(datafeed.close, period = self.params.sma1);
            self.myInds[datafeed]["sma2"] = bt.indicators.SimpleMovingAverage(datafeed.close, period = self.params.sma2);
            self.myInds[datafeed]["cross"] = bt.indicators.CrossOver(self.myInds[datafeed]["sma1"], self.myInds[datafeed]["sma2"]);

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

                # If the short SMA crossed over the long SMA then GO LONG!!
                if self.myInds[datafeed]["cross"][0] == 1:
                    print(datafeed._name + " - The sma1 just crossed the sma2 - BUY!!!!");
                    print(datafeed._name + " - The sma1 is now: ", self.myInds[datafeed]["sma1"][0]);
                    print(datafeed._name + " - The sma2 is now: ", self.myInds[datafeed]["sma2"][0]);
                    self.buy(datafeed, size = 100);

                # If the long SMA crossed over the short SMA then GO SHORT!!
                elif self.myInds[datafeed]["cross"][0] == -1:
                    print(datafeed._name + " - The sma2 just crossed the sma1 - SHORT!!!!");
                    print(datafeed._name + " - The sma1 is now: ", self.myInds[datafeed]["sma1"][0]);
                    print(datafeed._name + " - The sma2 is now: ", self.myInds[datafeed]["sma2"][0]);
                    self.sell(datafeed, size = 100);
            else:
                # If the short SMA crossed over the long SMA then CLOSE OUT YOUR SHORT AND GO LONG!!
                if self.myInds[datafeed]["cross"][0] == 1:
                    print(datafeed._name + " - The sma1 just crossed the sma2 - CLOSE SHORT AND GO LONG!!!!");
                    print(datafeed._name + " - The sma1 is now: ", self.myInds[datafeed]["sma1"][0]);
                    print(datafeed._name + " - The sma2 is now: ", self.myInds[datafeed]["sma2"][0]);
                    self.close(datafeed);
                    self.buy(datafeed, size = 100)

                # If the long SMA crossed over the short SMA then CLOSE OUT YOUR LONG AND GO SHORT!!
                elif self.myInds[datafeed]["cross"][0] == -1:
                    print(datafeed._name + " - The sma2 just crossed the sma1 - CLOSE LONG AND GO SHORT!!!!");
                    print(datafeed._name + " - The sma1 is now: ", self.myInds[datafeed]["sma1"][0]);
                    print(datafeed._name + " - The sma2 is now: ", self.myInds[datafeed]["sma2"][0]);
                    self.close(datafeed);
                    self.sell(datafeed, size = 100);

if __name__ == '__main__':
    # Create Cerebro entity
    cerebro = bt.Cerebro();

    # Add Strategy
    cerebro.addstrategy(TestStrategy);

    # Create a Data Feeds
    yahooList = [("ORCL", "Oracle Stock"),
                    ("AAPL", "Apple Stock"),
                    ("MSFT", "Microsoft Stock"),
                    ("INTC", "Intel Stock")
                ];

    for stock in yahooList:

        newDataFeed = bt.feeds.YahooFinanceData(
            dataname = stock[0],
            # Do not pass values before this date
            fromdate = datetime.datetime(2000, 1, 1),
            # Do not pass values after this date
            todate = datetime.datetime(2010, 1, 1),
            reverse = False
        );

        # Add the Data Feed to Cerebro
        cerebro.adddata(newDataFeed, stock[1]);

    # Set our desired cash start
    cerebro.broker.setcash(100000.00);
    cerebro.broker.setcommission(commission=0.00);

    print("Starting Portfolio: %.2f" % cerebro.broker.getvalue())

    cerebro.run();

    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue());

    cerebro.plot();
