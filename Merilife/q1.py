class Solution:
    def pushDominoes(self, d: str) -> str:
        ans = ""
        i = 0
        time = [float("inf") for i in range(len(d))]
        old = d
        i = 0
        d = list(d)
        posh = [0 for i in range(len(d))]
        for i in range(len(d)):
            if d[i] == "R":
                j = i+1
                while j < len(d):
                    posh[j] = 1
                    j+=1
                break
        posh2 = [0 for i in range(len(d))]  
        for i in range(len(d)-1, -1, -1):
            if d[i] == "L":
                j = i-1
                while j >= 0:
                    posh2[j] = 1
                    j-=1
                break
        i = 0
        while i < len(d):
            if d[i] == "L":
                j = i-1
                # t  = 1
                if old[i] == "L":
                    time[i] = 0
                t = time[i]+1
                f = 0
                while j >= 0 and  t < time[j] and old[j] != "R":
                    d[j] = "L"
                    time[j] = t
                    t+=1
                    j-=1
                if j >= 0 and time[j] == t and posh[j] == 1 and old[j] == ".":
                    d[j] = "."
                # print(time)
            elif d[i] == "R":
                j = i+1
                # t  = 1
                # time[i] = 0
                if old[i] == "R":time[i] = 0
                t = time[i]+1
                # breakpoint()
                while j < len(d) and  t < time[j] and old[j] != "L":
                    d[j] = "R"
                    time[j] = t
                    t+=1
                    j+=1
                if j < len(d) and time[j] == t and posh2[j] == 1 and old[j] == ".":
                    d[j] = "."
            i+=1
        print(time)
        return "".join(d)
    

a = Solution()
print(a.pushDominoes("RR.L"))
print(a.pushDominoes("..R..")) # "LL.RR.LLRRLL.."


# Time Complexity: 
# it is 