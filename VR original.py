import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

입력티커 = input("티커를 입력하세요 (종료: quit): ")
시작일자 = input("시작일자를 입력하세요 (yyyy-mm-dd): ")
종료일자 = input("종료일자를 입력하세요 (yyyy-mm-dd): ")

기울기 = input("Gradient를 입력하세요 (5~100): ")
초기P비율 = input("초기 Pool 비율 몇인가요? (0.0~1.0) : ")
상한율 = input("상한 밴드 범위는 몇인가요? (0.1~0.2) : ")
하한율 = input("하한 밴드 범위는 몇인가요? (0.1~0.2) : ")
기초자산 = input("기초자산 몇 달러인가요?: ")
적립금 = input("10영업일마다 적립금은 몇 달러로 할까요? : ")

print('시작 확인')

종목티커 = yf.download(입력티커, start=시작일자, end=종료일자)

print('데이터 가져오기 확인')

G = int(기울기)
rootG= np.sqrt(G)
초기P비율 = float(초기P비율) # 초기P비율을 문자열에서 실수로 바꾸어줌
상한율 = float(상한율) # 상하한율을 문자열에서 실수로 바꾸어줌
하한율 = float(하한율) # 상하한율을 문자열에서 실수로 바꾸어줌
기초자산 = int(기초자산) # 기초자산을 문자열에서 정수로 바꾸어줌
적립금 = int(적립금)
기초원금 = 기초자산

V = (1 - 초기P비율) * 기초자산 # 초기 V값은 90%로 시작
P = 초기P비율 * 기초자산 # 초기 Pool은 10%로 시작
Vmax = (1 + 상한율) * V
Vmin = (1 - 하한율) * V

고가리스트 = 종목티커['High'] # ticker데이터세트에서 고가리스트만 불러옴
저가리스트 = 종목티커['Low'] # ticker데이터세트에서 저가리스트만 불러옴
시가리스트 = 종목티커['Open'] # ticker데이터세트에서 시가리스트만 불러옴
종가리스트 = 종목티커['Adj Close'] # ticker데이터세트에서 종가리스트만 불러옴

매매일수 = len(종가리스트) # 아래 for문을 작동시키기 위해 길이를 측정함
사이클끝 = int(매매일수/10)*10
종가리스트 = 종목티커['Adj Close'][0:사이클끝]
    
Vmax리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
Vmin리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
V리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
E리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
P리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
EP리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
zero리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
TQ전고점리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
EP전고점리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
TQMDD리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
EPMDD리스트 = 종목티커['Adj Close'][0:사이클끝].copy()
    
초일종가 = round(종가리스트[0], 2)  # 종가리스트에서 첫번째 데이터 즉 초일종가를 불러옴
말일종가 = round(종가리스트[-1], 2) # 종가리스트에서 사이클 마지막 데이터 즉 사이클 말일종가를 불러옴
    
현재개수 = int(V/초일종가) # 시작할 때 현재개수는 종가매매임
    
E = 현재개수 * 초일종가
    
#수익률 계산을 위한 영업일수와 투자연수
영업일수 = 250
투자연수 = 매매일수 / 영업일수

#VR 구현
for i in range(0, int(매매일수/10)):  # 매매일수를 10으로 나눈만큼 for문 돌림. 즉 10일에 한 번 for 문 돌림.
    P2 = 0.5 * P # 거치식은 0.5, 적립식은 0.75, 인출식은 0.25
    P3 = 0.5 * P # 거치식은 0.5, 적립식은 0.25, 인출식은 0.75
    for j in range (i*10, i*10+10):
        while 현재개수 * 고가리스트[j] >= Vmax: # 매도
            P3 = P3 + (Vmax/현재개수)
            현재개수 = 현재개수 - 1
        while 현재개수 * 저가리스트[j] <= Vmin: # 매수
            if P2 >= 저가리스트[j]:
                if P2 >= (Vmin/현재개수):
                    P2 = P2 - (Vmin/현재개수)
                else:
                    P2 = P2 - 종가리스트[j]
                현재개수 = 현재개수 + 1
            else:
                break
        Vmax리스트[j] = Vmax
        Vmin리스트[j] = Vmin
        V리스트[j] = V
        E리스트[j] = 현재개수 * 종가리스트[j]
        P리스트[j] = P3 + P2
        EP리스트[j] = 현재개수 * 종가리스트[j] + P3 + P2
        zero리스트[j] = 0
    P = P3 + P2
    E = 현재개수 * 종가리스트[i*10+9]
    V = V + (P/G) + (E-V)/(2*rootG) + 적립금
    기초원금 = 기초원금 + 적립금
    Vmax = (1 + 상한율) * V
    Vmin = (1 - 하한율) * V   

#TQ전고점리스트 생성
for i in range(0, 사이클끝):
        if i == 0:
            TQ전고점리스트[i] = 종가리스트[i]
        else:
            if 종가리스트[i] > TQ전고점리스트[i-1]:
                TQ전고점리스트[i] = 종가리스트[i]
            else:
                TQ전고점리스트[i] = TQ전고점리스트[i-1]
                
#EP전고점리스트 생성
for i in range(0, 사이클끝):
        if i == 0:
            EP전고점리스트[i] = EP리스트[i]
        else:
            if EP리스트[i] > EP전고점리스트[i-1]:
                EP전고점리스트[i] = EP리스트[i]
            else:
                EP전고점리스트[i] = EP전고점리스트[i-1]

#TQMDD리스트 생성
for i in range(0, 사이클끝):
    if i == 0:
        TQMDD리스트[i] = 0
    else:
        if TQ전고점리스트[i] == TQ전고점리스트[i-1] :
            TQMDD리스트[i] = - (TQ전고점리스트[i] - 종가리스트[i]) / TQ전고점리스트[i]
        else :
            TQMDD리스트[i] = 0
            
#EPMDD리스트 생성
for i in range(0, 사이클끝):
    if i == 0:
        EPMDD리스트[i] = 0
    else:
        if EP전고점리스트[i] == EP전고점리스트[i-1] :
            EPMDD리스트[i] = - (EP전고점리스트[i] - EP리스트[i]) / EP전고점리스트[i]
        else :
            EPMDD리스트[i] = 0
    
print('for문 완료 확인, 그림 그리기 시작')    
    
기말자산 = 현재개수 * 종가리스트[-1] + P
        
총수익비 = 기말자산 / 기초원금
총수익률 = round(100 * (총수익비 - 1), 2)
연수익비 = (총수익비 ** (1/투자연수)) - 1
연수익률 = round(100 * 연수익비, 2)
존버수익률 = round(100 * (말일종가 - 초일종가) / 초일종가, 2)
존버기말자산 = round(int(기초자산/초일종가) * 말일종가, 2)
    
투자연수 = round(투자연수, 2)
기말자산 = round(기말자산, 2)    

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.plot((기초자산/초일종가)*종가리스트, color='lightgray', linewidth=0.1)
ax1.plot(Vmax리스트, color='orange', linewidth=0.1)
ax1.plot(Vmin리스트, color='orange', linewidth=0.1)
# ax1.plot(V리스트, color='lightgray', linewidth=0.1)
# ax1.plot(E리스트, color='lightcoral', linewidth=0.1)
ax1.plot(P리스트, color='cyan', linewidth=0.1)
ax1.plot(EP리스트, color='lightcoral', linewidth=0.1)
ax1.plot(zero리스트, color='black', linewidth=0.1)
# ax2.plot(TQMDD리스트, color='purple', linewidth=0.1)
ax2.plot(EPMDD리스트, color='lightgray', linewidth=0.1)

# plt.yscale('log')
ax1y = ax1.get_yticks()
ax1.set_yticklabels(['{:,.0f}'.format(x) for x in ax1y])

ax2y = ax2.get_yticks()
ax2.set_yticklabels(['{:,.0%}'.format(x) for x in ax2y])

plt.gca().spines['right'].set_visible(False) #오른쪽 테두리 제거
plt.gca().spines['top'].set_visible(False) #위 테두리 제거

파일이름 = input("파일이름을 입력하세요 (test.png): ")
plt.savefig(파일이름, dpi=300)

V = round(V, 2)
E = round(E, 2)
P = round(P, 2)

print(f'\n투자연수: {투자연수}년({매매일수}일), 기초자산: {기초자산}달러, 기초원금: {기초원금}달러, 적립금: {적립금}달러')
print(f'초일종가: {초일종가}달러, 말일종가: {말일종가}달러, 존버수익률: {존버수익률}%, 존버기말자산: {존버기말자산}달러')
print(f'연수익률: {연수익률}%, 총수익률: {총수익률}%, 기말자산: {기말자산}달러')
print(f'V값: {V}달러, E값: {E}달러, P값: {P}달러')