INSERT INTO dimensions (name, name_aliases, weight) VALUES ('processes', 'p,process', 5);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (1, 'fast', 'f',    0);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (1, 'typical', 't', 1);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (1, 'slow', 's'   , 0);

INSERT INTO dimensions (name, name_aliases, weight) VALUES ('temperatures', 't,temp,temperature', 4);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (2, 'hot', 'h',     0);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (2, 'ambient', 'a', 1);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (2, 'cold', 'c'   , 0);

INSERT INTO dimensions (name, name_aliases, weight) VALUES ('voltages', 'v,volt,voltage', 2);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (3, 'high', 'h',    0);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (3, 'typical', 't', 1);
INSERT INTO dimension_values (dimension_id, value, value_aliases, `default`) VALUES (3, 'low', 'l'    , 0);



INSERT INTO data_requests (created_by, type, subject, execution_status, priority, deadline, estimated_completion_date) VALUES ('jordug01', 'DEBUG', '65nm_fuji', 0, 0, '2007-12-25 00:00:00', '2007-12-22 00:00:00');

INSERT INTO data_request_dimension_values (data_request_id, dimension_value_id) VALUES (1, 1);
INSERT INTO data_request_dimension_values (data_request_id, dimension_value_id) VALUES (1, 6);
INSERT INTO data_request_dimension_values (data_request_id, dimension_value_id) VALUES (1, 7);
INSERT INTO data_request_dimension_values (data_request_id, dimension_value_id) VALUES (1, 8);



INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('Agilent Technologies', '81134A', '3.35 GHz Pulse/Pattern Generator', '', 'Pattern Generator', '2008-01-01 00:00:00', '2008-01-01 00:00:00');
INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('BERTScope', '12500A', 'Bit Error Analyzer', '', 'Bertscope', '2008-01-01 00:00:00', '2008-01-01 00:00:00');
INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('BERTScope', '7500A', 'Bit Error Analyzer', '', 'Bertscope', '2008-01-01 00:00:00', '2008-01-01 00:00:00');
INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('Keithley Instruments', '2400 Series', 'Digital Source Meter', '', 'Multimeter', '2008-01-01 00:00:00', '2008-01-01 00:00:00');
INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('LeCroy', 'SDA100G', 'Digital Sampling Oscilloscope', '', 'Oscilloscope', '2008-01-01 00:00:00', '2008-01-01 00:00:00');
INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('Tektronix', 'CSA8000', 'Digital Sampling Oscilloscope', '', 'Oscilloscope', '2008-01-01 00:00:00', '2008-01-01 00:00:00');
INSERT INTO lab_assets (manufacturer, model, type, part_code, asset_class, created_at, updated_at) VALUES ('Tektronix', 'TDS8000', 'Digital Sampling Oscilloscope', '', 'Oscilloscope', '2008-01-01 00:00:00', '2008-01-01 00:00:00');



