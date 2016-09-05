from manipulator.manipulator import Manipulator

tor_cmd = "service tor restart"

reporter = Manipulator(tor_cmd)
reporter.test()
