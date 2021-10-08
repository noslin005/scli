# -*- encoding: utf8 -*-
#
# Collection of methods to interact with Source Code Scheduler API
#
from app import utils
from app import base, exception

__author__ = "Nilson Lopes"


class API(base.BaseAPI):

    def __init__(self, auth_token: str):
        super(API, self).__init__(auth_token)

    def send_post(self, payload: dict):
        '''send an HTTP POST '''
        return super(API, self).send_post(payload)

    def system_search(self, serials: list):
        '''Lookup a system's ID and Serial using component serial numbers

        Args:
            serials (list): A list of system components serial numbers

        Returns:
            dict: with the systemid and serial keys
            None: if no maches is found.

        Sample Return:
            {"status":"success",
             "message":"unique match system serial number 1107774-1",
             "systemid":"171376",
             "serial":"1107774-1"
            }
        '''
        payload = {
            "type": "SystemSearch",
            "serials": serials
        }
        try:
            data = self.send_post(payload=payload)
        except exception.APIError as ex:
            self.logger.debug(ex)
        else:
            return data

    def get_system_id(self, system_serial: str):
        '''Lookup a system's ID by system serial number.
        Use this if SystemSearch fails and you have to
        prompt a user for manual lookup.

        Args:
            system_serial (str): a valid system serial number
        '''
        system_serial = utils.normalize_serial(system_serial)
        payload = {
            'type': 'SystemID',
            'serial': system_serial
        }
        try:
            data = self.send_post(payload=payload)
        except exception.APIError as ex:
            self.logger.debug(ex)
        else:
            return data['systemid']

    def get_all_system_id(self, system_serial: str):
        '''On a order with muliple systems,
        this method uses the system serial to return
        a list of a tuple (serial, systemid) for every
        system in this order.

        Args:
            system_serial (str): a valid system serial number
        '''
        base_system = system_serial.split('-')[0]
        all_systems = []
        count = 1
        while True:

            next_system = f"{base_system}-{count}"
            system_id = self.get_system_id(next_system)
            formated_serial = f"{base_system}-{count:02d}"
            if not system_id:
                break
            else:
                all_systems.append((formated_serial, system_id))
            count += 1

        return all_systems

    def get_system_lot_serial(self, system_id: int, rule=""):
        '''Returns data from the scheduler's lotserial entry page.
        Includes both sage100 valuation and custom required fields.
        The rule parameter is added in order to filter the output
        to include only quested field, for example 'IPMI Password'
        or 'MAC Address'.

        Args:
            system_id (int): a unique valid system id
            rule (str): Valid scheduler Lot Serial field, used
                        to filter the output.
        '''
        payload = {
            "type": "SystemGetDataLotSerial",
            "system": system_id
        }
        if rule:
            payload.update({'rule': rule})
        try:
            results = self.send_post(payload=payload)
        except exception.APIError as e:
            self.logger.debug(e)
            return

        if rule:
            try:
                return results['data'][0]['LotSerial']
            except (KeyError, IndexError):
                self.logger.debug(
                    f"no data for '{rule}' could be found")
                return
        else:
            return results['data']

    def get_ipmi_mac_address(self, system_id: int):
        '''Get the system IPMI MAC Address
        '''
        rule = "MAC Address"
        return self.get_system_lot_serial(system_id, rule=rule)

    def get_ipmi_password(self, system_id: int):
        '''Get the system IPMI Password
        '''
        rule = "IPMI Password"
        return self.get_system_lot_serial(system_id, rule=rule)

    def get_sum_partno(self, system_id: int):
        '''Checks if a system includes a SUM key license.

        Args:
            system_id (int): a unique valid system id

        Returns:
            str: the assigned sum part number
        '''
        payload = {
            "type": "SumLookup",
            "system": system_id
        }
        try:
            results = self.send_post(payload=payload)
        except exception.APIError as e:
            self.logger.debug(e)
            return
        try:
            expected_license = results['expected_licenses']
        except (KeyError, IndexError):
            self.logger.debug(
                f'system {system_id}: error while checking sum license')
            return

        if not expected_license:
            self.logger.debug(
                f'system {system_id}: has no SUM license assigned')
            return
        try:
            licenses = next(iter(results['licenses']))
            return licenses['partno']
        except KeyError:
            return

    def generate_sum_license(self, system_id: int, mac: str, partno: str):
        '''Reserves and returns a sum key license

        Args:
            system_id (int): a unique valid system id
            mac (str): a valid mac address
            partno (str): the assigned sum license partno for this system

        Returns:
            str: returns a sum key license
        '''
        payload = {
            "type": "SumAllocateKey",
            "system": system_id,
            "partno": partno,
            "mac": mac
        }
        try:
            results = self.send_post(payload=payload)
        except exception.APIError as e:
            self.logger.debug(e)
        else:
            return results['productkey']

    def apply_sum_license(self, system_id: int, mac: str):
        '''Marks an allocated sum license key as applied.

        Args:
            system_id (int): a unique valid system id
            mac (str): a valid mac address
        '''
        payload = {
            "type": "SumApplyKey",
            "system": system_id,
            "mac": mac
        }
        try:
            results = self.send_post(payload=payload)
        except exception.APIError as e:
            self.logger.debug(e)
        else:
            self.logger.debug(results['message'])
            return True

    def get_license_by_system_id(self, system_id, system_serial):
        """Uses the system_id to retrieve a list of fields
        for a given system. The fields include the IPMI MAC Address,
        IPMI Password, License Key and Serial Number.
        """
        ipmi_mac = self.get_ipmi_mac_address(system_id)
        # if not ipmi_mac:
        #     return
        ipmi_password = self.get_ipmi_password(system_id)
        license_partno = self.get_sum_partno(system_id)

        system_info = {'system_id': system_id,
                       'mac': ipmi_mac or 'N/A',
                       'user': 'ADMIN',
                       'password': ipmi_password or 'N/A',
                       'system_serial': system_serial
                       }

        if license_partno:
            license_key = self.generate_sum_license(system_id,
                                                    mac=ipmi_mac,
                                                    partno=license_partno)
            self.apply_sum_license(system_id, ipmi_mac)
            system_info.update({'sum_key': license_key})
        return system_info

    def get_license_by_system_serial(self, system_serial):
        """Uses the system_serial to retrieve a list of fields
        for a given system. The fields include the IPMI MAC Address,
        IPMI Password, License Key and Serial Number.
        """
        system_id = self.get_system_id(system_serial)
        if not system_id:
            return
        ipmi_mac = self.get_ipmi_mac_address(system_id)
        ipmi_password = self.get_ipmi_password(system_id)
        license_partno = self.get_sum_partno(system_id)

        system_info = {'system_id': system_id,
                       'mac': ipmi_mac or 'N/A',
                       'user': 'ADMIN',
                       'password': ipmi_password or 'N/A',
                       'system_serial': system_serial
                       }
        if license_partno:
            license_key = self.generate_sum_license(system_id,
                                                    mac=ipmi_mac,
                                                    partno=license_partno)
            self.apply_sum_license(system_id, ipmi_mac)
            system_info.update({'sum_key': license_key})

        return system_info

    def get_multi_serials(self, system_id, rule=None):
        """Given a field, returns all serial number 
        currents scanned in.

        This is for Quads system which MACs/Password
        are scanned per System
        """
        payload = {
            "type": "SystemGetDataLotSerial",
            "system": system_id,
            "rule": rule
        }
        try:
            results = self.send_post(payload=payload)
        except BaseException as e:
            self.logger.error(e)

        data = []
        try:
            for serial in results['data']:
                data.append(serial['LotSerial'])
        except (KeyError, IndexError):
            self.logger.error(
                f"no data for '{rule}' could be found")
        else:
            return data

    def get_multi_keys(self, system_serial):
        system_id = self.get_system_id(system_serial)
        if not system_id:
            return
        ipmi_mac = self.get_multi_serials(system_id, rule='MAC Address')
        ipmi_password = self.get_multi_serials(system_id, rule='IPMI Password')
        license_partno = self.get_sum_partno(system_id)
        data = [a for a in zip(ipmi_mac, ipmi_password)]

        all_system = []
        for mac, passwd in data:
            license_key = self.generate_sum_license(system_id,
                                                    mac=ipmi_mac,
                                                    partno=license_partno)
            system_info = {'system_id': system_id,
                           'mac': ipmi_mac,
                           'user': 'ADMIN',
                           'password': ipmi_password,
                           'system_serial': system_serial,
                           'sum_key': license_key
                           }
            all_system.append(system_info)
        return all_system
