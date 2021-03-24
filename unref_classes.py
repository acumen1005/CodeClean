# -*- coding:utf-8 -*-
#!/usr/bin/python

import os
import re

class UnrefClassesHandler(object):
    
    def __init__(self, path):
        self.symbols = {}
        self.ref_classes = set()
        self.all_classes = set()
        self.path = path

    # add white list eg: third-party
    def prefix_whitelist(self):
        return ['PodsDummy_', 'RCT', 'TuSDK', 'JSQ', 'RAC', 'DOU',
         'Alibc', 'GPUImage', 'JCORE', 'QQ', '_', 'UM', 'Baidu', 'JWT',
         'DT', 'AliBC', 'WBSDK', 'WB', 'WV', 'WX']

    def is_in_whitelist(self, symbol):
        for p in self.prefix_whitelist():
            if symbol.startswith(p):
                return True
        return False

    def pre_handle(self):
        self.symbols = self.class_symbols()
        self.ref_classes = self.class_all()
        self.all_classes = self.class_ref()

    def solve(self):
        # diff
        self.all_classes.symmetric_difference
        diff_classes = self.ref_classes.difference(self.all_classes)
        count = 0
        for c in diff_classes:
            symbol = self.symbols[c]
            if not self.is_in_whitelist(symbol):
                print symbol
                count += 1
        print 'total: ', len(diff_classes)
        print 'real unref classes count: ', count

    def rebase_pointers(self, line):
        line = line[16:].strip().split(' ')
        if not line or len(line) < 4:
            return
        pointers = set()
        pointers.add(line[1] + line[0])
        pointers.add(line[3] + line[2])
        return pointers

    def class_symbols(self):
        symbols = {}
        # expampe: 0000000103113f68 (__DATA,__objc_data) external _OBJC_CLASS_$_EpisodeStatusDetailItemView
        ref_class_name = re.compile('(\w{16}) .* _OBJC_CLASS_\$_(.+)')
        lines = os.popen('nm -nm %s' % self.path).readlines()
        for line in lines:
            result = ref_class_name.findall(line)
            if result:
                (addr, symbol) = result[0]
                symbols[addr] = symbol
        return symbols
        

    def class_ref(self):
        ref_pointers = set()
        lines = os.popen('/usr/bin/otool -v -s __DATA __objc_classrefs %s' % self.path).readlines()
        # expampe: 000000010184f208        018a2258 00000001 018a2550 00000001
        for line in lines:
            pointers = self.rebase_pointers(line)
            if not pointers:
                continue
            ref_pointers = ref_pointers.union(pointers)
        return ref_pointers

    def class_all(self):
        all_pointers = set()
        lines = os.popen('/usr/bin/otool -v -s __DATA __objc_classlist %s' % self.path).readlines()
        # expampe: 000000010184f208        018a2258 00000001 018a2550 00000001
        for line in lines:
            pointers = self.rebase_pointers(line)
            if not pointers:
                continue
            all_pointers = all_pointers.union(pointers)
        return all_pointers
    

if __name__ == '__main__':
    path = raw_input('Please input binary path\nFor example:xxx/xxx.app/xxx\n').strip()
    handler = UnrefClassesHandler(path)
    handler.pre_handle()
    handler.solve()