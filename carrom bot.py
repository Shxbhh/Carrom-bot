from math import sqrt,atan,degrees
from random import randint
import cv2 # type: ignore
import numpy as np # type: ignore
import serial # type: ignore
import time

radius=0
k=radius

#colour range, radius, and Hough Transform parameters for black and white coins
minR=11
maxR=14
p1=100 # First parameter for Hough Transform (Canny edge threshold)
p2=12 # Second parameter for Hough Transform (circle center detection threshold)
minD=minR # Minimum distance between detected circles (for Hough Transform)
pocketParam=5
tolerance=0.9

#same params for red coins
RminR=3
RmaxR=10
RminD=RminR

#global variables to store colors(b,g,r)e
colors=[]
colorRed=[]
colorBlack=[]
colorWhite=[]
rangeRedEnd = [[0, 0], [0, 0]]  # Stores red color range
rangeBW = [[0, 0], [0, 0, 0]]  # Stores black & white color range
rangeB = [[0, 0], [0, 0]]  # Stores black coin range
rangeW = [[0, 0], [0, 0]]  # Stores white coin range

#global for coordinates of pockets	
pockets=[]

#calibration flag
calib=1

#create serial object and variable for serial reading
ser=serial.Serial('/dev/ttyACM0', 9600)  #'/dev/ttyACM0' is the  serial port address where the Arduino is connected
buttonPress=ser.read()
print (buttonPress)

#consider the board to be a 1000 x 1000 grid
pocket1_x=0
pocket1_y=0
pocket2_x=1000
pocket2_y=0
pocket3_x=1000
pocket3_y=1000
pocket4_x=0
pocket4_y=1000

#striker parameters
strikerLine_y=0 #Stores the Y-coordinate of the striker's starting position.
strikerLine=[]  #Stores the coordinates of the striker's movement.
strikerLineEnds=[0,0] #Stores the start and end points of the striker.
strikerLine_End=0
strikerLine_Start=0
striker_radius=0

#mouse callback functions, for pockets, red/color and BW
def get_values(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDOWN:
		colors.append([q[y,x,0],q[y,x,1],q[y,x,2]])

def get_coords(event,x,y,flags,param):
 	if event == cv2.EVENT_LBUTTONDOWN:
		 pockets.append([y,x])

def get_coords_strikerLine(event,x,y,flags,param):
 	if event == cv2.EVENT_LBUTTONDOWN:
		 strikerLine.append([y,x])

#for creating a window, binding the function to it, and showing the image in it
def show_Window(purpose):
	cv2.namedWindow(purpose)
	cv2.setMouseCallback(purpose,get_values)
	while(1):
		cv2.imshow(purpose,p)
		if cv2.waitKey(20) & 0xFF == 27 :
			break
	cv2.destroyAllWindows()

def show_Window_coords(purpose):
	cv2.namedWindow(purpose)
	cv2.setMouseCallback(purpose,get_coords)
	while(1):
		cv2.imshow(purpose,p)
		if cv2.waitKey(20) & 0xFF == 27 :
			break
	cv2.destroyAllWindows()

def show_Window_coords_strikerLine(purpose):
	cv2.namedWindow(purpose)
	cv2.setMouseCallback(purpose,get_coords_strikerLine)
	while(1):
		cv2.imshow(purpose,p)
		if cv2.waitKey(20) & 0xFF == 27 :
			break
	cv2.destroyAllWindows()

#calculating ranges for red, black, white coins
def calc_Range(array):
	big=0
	small=0
	for a in range(0,len(array[0])-1) :
		big=array[0][a]
		small=array[0][a]
		for b in range(0, len(array)) :
			big=max(big,array[b][a])
			small=min(small,array[b][a])
		rangeRedEnd[0][a]+=2*big-small
		rangeRedEnd[1][a]+=2*small-big

def calc_Range_BW(array):
	big=0
	small=0
	for a in range(0,len(array[0])-1) :
		big=array[0][a]
		small=array[0][a]
		for b in range(0, len(array)) :
			big=max(big,array[b][a])
			small=min(small,array[b][a])
		rangeBW[0][a]+=big+tolerance*(big-small)
		rangeBW[1][a]+=small-tolerance*(big-small)

#best-fit square from selected pocket centres
def make_Square(array):
	#calculating the average x and y positions of the pockets
    avgx = sum(i[0] for i in pockets) / 4
    avgy = sum(i[1] for i in pockets) / 4
	#calculating the deviation of pockets from the mean posn
    devx = sum(abs(i[0] - avgx) for i in pockets) / 4
    devy = sum(abs(i[1] - avgy) for i in pockets) / 4
    return [[avgx-devx, avgy-devy], [avgx+devx, avgy-devy], [avgx+devx, avgy+devy], [avgx-devx, avgy+devy]]

def isPointAroundPocket(point,pocketArray):
	pass

#AI.py functions
def isOnLine(x):
	if x>strikerLine_Start and x <strikerLine_End:
		return True
	return False

class Coin:
	#Class that takes care of coins
	radius = k
	
	def __init__(self,xcord,ycord):
		self.x = xcord
		self.y = ycord
		self.slope1 = (self.y-pocket1_y)/float((self.x-pocket1_x))
		self.slope2 = (self.y-pocket2_y)/float((self.x-pocket2_x))
		self.slope3 = (self.y-pocket3_y)/float((self.x-pocket3_x))
		self.slope4 = (self.y-pocket4_y)/float((self.x-pocket4_x))
		self.intercept1= self.y - self.slope1*self.x 
		self.intercept2= self.y - self.slope2*self.x 
		self.intercept3= self.y - self.slope3*self.x 
		self.intercept4= self.y - self.slope4*self.x

	def getx(self):
		return self.x
	def gety(self):
		return self.y
	def getCord(self):
		return (self.x,self.y);
	def setCord(self,xcord,ycord):
		self.x=xcord
		self.y=ycord
		self.slope1 = (self.y-pocket1_y)/float((self.x-pocket1_x))
		self.slope2 = (self.y-pocket2_y)/float((self.x-pocket2_x))
		self.slope3 = (self.y-pocket3_y)/float((self.x-pocket3_x))
		self.slope4 = (self.y-pocket4_y)/float((self.x-pocket4_x))
		self.intercept1= self.y - self.slope1*self.x 
		self.intercept2= self.y - self.slope2*self.x
		self.intercept3= self.y - self.slope3*self.x
		self.intercept4= self.y - self.slope4*self.x
	

class WhiteCoin(Coin):
	def __init__(self,xcord,ycord):
		Coin.__init__(self,xcord,ycord)
	def printCoin(self):
		print("White" + " coin present at " + str(Coin.getx(self)) +" , " + str(Coin.gety(self)))

class BlackCoin(Coin):
	def __init__(self,xcord,ycord):
		Coin.__init__(self,xcord,ycord)
	def printCoin(self):
		print("Black" + " coin present at " + str(Coin.getx(self)) +" , " + str(Coin.gety(self)))

class RedCoin(Coin):
	def __init__(self,xcord,ycord):
		Coin.__init__(self,xcord,ycord)
	def printCoin(self):
		print("Queen" + " coin present at " + str(Coin.getx(self)) +" , " + str(Coin.gety(self)))

listOfWhiteCoins = [WhiteCoin(900,50) for i in range(1)]
listOfBlackCoins = [BlackCoin(100,100) for i in range(1)]
listOfRedCoins = [RedCoin(500,500) for i in range(1)]


def printAllCoins():
	for i in range (1):
		listOfWhiteCoins[i].printCoin()
		listOfBlackCoins[i].printCoin()
	listOfRedCoins[0].printCoin()

def isCoinInWay(coinToPot,striker_x,pocketnumber):
	if pocketnumber==1:
		slope=coinToPot.slope1
		intercept=coinToPot.intercept1
	elif pocketnumber==2:
		slope=coinToPot.slope2
		intercept=coinToPot.intercept2
	elif pocketnumber==3:
		slope=coinToPot.slope3
		intercept=coinToPot.intercept3
	elif pocketnumber==4:
		slope=coinToPot.slope4
		intercept=coinToPot.intercept4


	flag = 0 

	intercept1=intercept-(striker_radius+coinToPot.radius)*sqrt(1 + (slope**2))
	intercept2=intercept+(striker_radius+coinToPot.radius)*sqrt(1 + (slope**2))

	for coin in listOfWhiteCoins:
		if(coin!=coinToPot and coin.gety()<coinToPot.radius +strikerLine_y):
			if ((coin.gety()-slope* coin.getx()-intercept1)*(coin.gety()-slope* coin.getx()-intercept2)) <= 0:
				flag = flag+1
				x=coin.getx()
				y=coin.gety()

	for coin in listOfBlackCoins:
		if(coin!=coinToPot and coin.gety()<coinToPot.radius +strikerLine_y):
			if ((coin.gety()-slope* coin.getx()-intercept1)*(coin.gety()-slope* coin.getx()-intercept2)) <= 0:
				flag = flag+1
				x=coin.getx()
				y=coin.gety()

	for coin in listOfRedCoins:
		if(coin!=coinToPot and coin.gety()<coinToPot.radius +strikerLine_y):
			if ((coin.gety()-slope* coin.getx()-intercept1)*(coin.gety()-slope* coin.getx()-intercept2)) <= 0:
				flag = flag+1
				x=coin.getx()
				y=coin.gety()

	if flag==1:
		return flag,x,y 
	return flag,0,0


def directShot(coinToPot):  #Checks if a coin can be directly potted.
	strikerLine_x1 = (strikerLine_y - coinToPot.gety())/coinToPot.slope1 + coinToPot.getx();
	if(isOnLine(strikerLine_x1)):
		flag,xcord,ycord=isCoinInWay(coinToPot,strikerLine_x1,1);
		if(flag==0):
			if degrees(atan(coinToPot.slope1)) > 0:
				return True,strikerLine_x1,degrees(atan(coinToPot.slope1)),160;
			else:
				return True,strikerLine_x1,(180+degrees(atan(coinToPot.slope1))),160;

	strikerLine_x2 = (strikerLine_y - coinToPot.gety())/coinToPot.slope2 + coinToPot.getx();
	if(isOnLine(strikerLine_x2)):
		flag,xcord,ycord=isCoinInWay(coinToPot,strikerLine_x2,1);
		if(flag==0):
			if degrees(atan(coinToPot.slope2)) > 0:
				return True,strikerLine_x2,degrees(atan(coinToPot.slope2)),160;
			else:
				return True,strikerLine_x2,(180+degrees(atan(coinToPot.slope2))),160;

	return False,0,0,0;


def isCoinInRange(coinToPot,x1,y1,x2,y2):
	ymax= max(y1,y2);
	ymin=min(y1,y2);
	xmax= max(x1,x2);
	xmin=min(x1,x2);

	if(coinToPot.getx()<xmin):
		return False;
	if(coinToPot.getx()>xmax):
		return False;
	if(coinToPot.gety()<ymin):
		return False;
	if(coinToPot.getx()<ymax):
		return False;
	return True;

	

def isCoinInWay2(coinToPot,x1,y1,x2,y2): #checks for any obstructions

	slope = float(y2-y1)/float(x2-x1);
	intercept= y1- slope*x1;

	intercept1=intercept-(striker_radius+coinToPot.radius)*sqrt(1 + (slope**2))
	intercept2=intercept+(striker_radius+coinToPot.radius)*sqrt(1 + (slope**2))

	for coin in listOfWhiteCoins:
		if(coin!=coinToPot and coin.gety()<coinToPot.radius +strikerLine_y and isCoinInRange(coinToPot,x1,y1,x2,y2)):
			if ((coin.gety()-slope* coin.getx()-intercept1)*(coin.gety()-slope* coin.getx()-intercept2)) <= 0:
				return True;

	for coin in listOfBlackCoins:
		if(coin!=coinToPot and coin.gety()<coinToPot.radius +strikerLine_y and isCoinInRange(coinToPot,x1,y1,x2,y2)):
			if ((coin.gety()-slope* coin.getx()-intercept1)*(coin.gety()-slope* coin.getx()-intercept2)) <= 0:
				return True;

	for coin in listOfRedCoins:
		if(coin!=coinToPot and coin.gety()<coinToPot.radius +strikerLine_y and isCoinInRange(coinToPot,x1,y1,x2,y2)):
			if ((coin.gety()-slope* coin.getx()-intercept1)*(coin.gety()-slope* coin.getx()-intercept2)) <= 0:
				return True;

	return False;




def sideCollideShot(coinToPot): #calculates whether the striker can hit a coin such that it bounces off a side wall (board edge) and then goes into the pocket
	rightCollidePoint_y=(pocket2_x-pocket1_x)*coinToPot.slope1;
	strikerLine_x1 = (rightCollidePoint_y - strikerLine_y)/coinToPot.slope1 + pocket2_x;
	if(isOnLine(strikerLine_x1)):
		if(not isCoinInWay2(coinToPot,strikerLine_x1,strikerLine_y,pocket2_x,rightCollidePoint_y)):
			if(not isCoinInWay2(coinToPot,pocket2_x,rightCollidePoint_y,pocket1_x,pocket1_y)):
				if(degrees(atan(coinToPot.slope1)))>0:
					return True,strikerLine_x1,(180-degrees(atan(coinToPot.slope1))),200
				else:
					return True,strikerLine_x1,(-1)*degrees(atan(coinToPot.slope1)),200

	leftCollidePoint_y=(pocket1_x-pocket2_x)*coinToPot.slope2;
	strikerLine_x2 = (leftCollidePoint_y - strikerLine_y)/coinToPot.slope2 + pocket1_x;
	if(isOnLine(strikerLine_x2)):
		if(not(isCoinInWay2(coinToPot,strikerLine_x2,strikerLine_y,pocket1_x,leftCollidePoint_y) or isCoinInWay2(coinToPot,pocket1_x,leftCollidePoint_y,pocket2_x,pocket2_y))):
			if(degrees(atan(coinToPot.slope2)))<0:
				return True,strikerLine_x2,(-1)*degrees(atan(coinToPot.slope2)),200
			else:
				return True,strikerLine_x2,(180-degrees(atan(coinToPot.slope2))),200

	
	return False,0,0,0;




def cutShot(coinToPot): #checks if the striker can hit the coin at some angle(and not head-on)
	if(coinToPot.gety() > strikerLine_y):
		return False,0,0,0;
	if(coinToPot.getx()< pocket2_x/2):
		pointToHit_x = coinToPot.getx() + (coinToPot.radius + striker_radius)/sqrt(1 + coinToPot.slope1 **2);
		pointToHit_y = coinToPot.gety() + (coinToPot.radius + striker_radius)*coinToPot.slope1/sqrt(1 + coinToPot.slope1 **2);
		strikerLine_x1 = pointToHit_x + (strikerLine_y - pointToHit_y)/coinToPot.slope1*1.5;
		strikerLine_x2 = pointToHit_x + (strikerLine_y - pointToHit_y)/coinToPot.slope1*0.5;
		m1=(pointToHit_y-strikerLine_y)/float(pointToHit_x-strikerLine_x1)
		m2=(pointToHit_y-strikerLine_y)/float(pointToHit_x-strikerLine_x2)
		if(isOnLine(strikerLine_x1)):
			if(not isCoinInWay2(coinToPot,strikerLine_x1,strikerLine_y,pointToHit_x,pointToHit_y)):
				if(not isCoinInWay2(coinToPot,pointToHit_x,pointToHit_y,pocket1_x,pocket1_y)):
					if m1>0:
						return True,strikerLine_x1,degrees(atan(m1)),180;
					else:
						return True,strikerLine_x1,(180+degrees(atan(m1))),180;
		if(isOnLine(strikerLine_x2)):
			if(not isCoinInWay2(coinToPot,strikerLine_x2,strikerLine_y,pointToHit_x,pointToHit_y)):
				if(not isCoinInWay2(coinToPot,pointToHit_x,pointToHit_y,pocket1_x,pocket1_y)):
					if m2>0:
						return True,strikerLine_x2,degrees(atan(m2)),180;
					else:
						return True,strikerLine_x2,(180+degrees(atan(m2))),180;

	else:
		pointToHit_x = coinToPot.getx() - (coinToPot.radius + striker_radius)/sqrt(1 + coinToPot.slope2 **2);
		pointToHit_y = coinToPot.gety() - (coinToPot.radius + striker_radius)*coinToPot.slope2/sqrt(1 + coinToPot.slope2 **2);
		strikerLine_x1 = pointToHit_x + (strikerLine_y - pointToHit_y)/coinToPot.slope2*1.5;
		strikerLine_x2 = pointToHit_x + (strikerLine_y - pointToHit_y)/coinToPot.slope2*0.5;
		m1=(pointToHit_y-strikerLine_y)/float(pointToHit_x-strikerLine_x1)
		m2=(pointToHit_y-strikerLine_y)/float(pointToHit_x-strikerLine_x2)
		if(isOnLine(strikerLine_x1)):
			if(not isCoinInWay2(coinToPot,strikerLine_x1,strikerLine_y,pointToHit_x,pointToHit_y)):
				if(not isCoinInWay2(coinToPot,pointToHit_x,pointToHit_y,pocket2_x,pocket2_y)):
					if m1>0:
						return True,strikerLine_x1,degrees(atan(m1)),180;
					else:
						return True,strikerLine_x1,(180+degrees(atan(m1))),180;
		if(isOnLine(strikerLine_x2)):
			if(not isCoinInWay2(coinToPot,strikerLine_x2,strikerLine_y,pointToHit_x,pointToHit_y)):
				if(not isCoinInWay2(coinToPot,pointToHit_x,pointToHit_y,pocket2_x,pocket2_y)):
					if m1>0:
						return True,strikerLine_x2,degrees(atan(m2)),180;
					else:
						return True,strikerLine_x2,(180+degrees(atan(m2))),180;

	return False,0,0,0;

#calibrate only once
if calib :
	#declare default camera object
	cap = cv2.VideoCapture(1)	
	time.sleep(1)
	# Capture a frame
	ret, p = cap.read()
	#release the resource
	cap.release()

#	p=cv2.imread('DirectShot2.jpg',-1)(alt for testing w/o physical camera)
	
	#read image as grayscale(Hough needs a single channel image)
	#j is grayscale, p is color(RGB), q is color(HSV)
	j=cv2.cvtColor(p,cv2.COLOR_BGR2GRAY) # Convert to grayscale
	q=cv2.cvtColor(p,cv2.COLOR_BGR2HSV) # Convert to HSV
	q=cv2.medianBlur(q,11)
	j=cv2.medianBlur(j,5)
	centrej=cv2.cvtColor(j,cv2.COLOR_GRAY2RGB)
	forRedAndShot=cv2.cvtColor(j,cv2.COLOR_GRAY2RGB)

	#read coordinates of pockets
	show_Window_coords('Click on all pockets')
	
	#read red, black and white colour arrays(b,g,r)
	#show_Window('Click on all the red ends')
	colorRed=colors
	colors=[]
	show_Window('Click on all the black coins')
	colorBlack=colors
	colors=[]
	show_Window('Click on all the white coins')
	colorWhite=colors
	colors=[]

	#calculating and displaying ranges of red ends, and black white coins
	#calc_Range(colorRed)
	calc_Range_BW(colorBlack)
	rangeB=rangeBW
	rangeBW=[[0,0],[0,0]]
	calc_Range_BW(colorWhite)
	rangeW=rangeBW
	rangeBW=[[0,0],[0,0]]

	#get the square from pockets for AI boundary
	square=make_Square(pockets)
	pocket2_x=square[3][1]-square[0][1]
	pocket3_x=square[2][1]-square[0][1]
	pocket3_y=square[2][0]-square[0][0]
	pocket4_y=square[1][0]-square[0][0]
	
	#find circles using the Hough Transform
	circles=cv2.HoughCircles(j,cv2.CV_HOUGH_GRADIENT,1,minD,param1=p1,param2=p2,minRadius=minR,maxRadius=maxR)
	circles=np.uint16(np.around(circles))
	circlesW=[]
	circlesB=[]
	redEnds=[]
	#show circles in green and centres in red
	#also classify coins based on the colors at their centres(values by calib)
	#and exclude the circles lying beyond the square formed by 4 pockets
	for i in circles[0, :] :
		cv2.circle(centrej,(i[0],i[1]),i[2],(0,255,0),2)
		cv2.circle(centrej,(i[0],i[1]),2,(0,255,0),3)
		if i[0]>(square[3][1]+pocketParam) or i[0]<(square[0][1]-pocketParam) :
			pass
		elif i[1]<(square[0][0]-pocketParam) or i[1]>(square[1][0]+pocketParam) :
			pass
		#elif q[i[1],i[0],1]>rangeRedEnd[1][1] and q[i[1],i[0],1]<rangeRedEnd[0][1] and q[i[1],i[0],0]>rangeRedEnd[1][0] and q[i[1],i[0],0]<rangeRedEnd[0][0] :
		#	redEnds.append([i[1]-square[0][0],i[0]-square[0][1]])
		elif q[i[1],i[0],1]>rangeB[1][1] and q[i[1],i[0],1]<rangeB[0][1] and q[i[1],i[0],0]>rangeB[1][0] and q[i[1],i[0],0]<rangeB[0][0]:
			circlesB.append([i[1]-square[0][0],i[0]-square[0][1]])
			radius+=i[2]
		elif q[i[1],i[0],1]>rangeW[1][1] and q[i[1],i[0],1]<rangeW[0][1] and q[i[1],i[0],0]>rangeW[1][0] and q[i[1],i[0],0]<rangeW[0][0]:
			circlesW.append([i[1]-square[0][0],i[0]-square[0][1]])
			radius+=i[2]

	radius=radius/(len(circlesW)+len(circlesB))
	striker_radius=radius*1.3
	
	
	
	show_Window_coords_strikerLine('Click on striker line ends')
	print (strikerLine_y)
	strikerLine_yF=(strikerLine[0][0]+strikerLine[1][0])/2
	strikerLineEnds[0]=min(strikerLine[0][1],strikerLine[1][1])
	strikerLineEnds[1]=max(strikerLine[0][1],strikerLine[1][1])
	strikerLine_y=int(strikerLine_yF)
	strikerLine_Start=int(strikerLineEnds[0])
	strikerLine_End=int(strikerLineEnds[1])
	strikerLine_y-=square[0][0]
	strikerLine_Start-=square[0][1]
	strikerLine_End-=square[0][1]	
	
	
	cv2.line(forRedAndShot,(strikerLine_Start,strikerLine_y),(strikerLine_End,strikerLine_y),(255,0,0),3)
	cv2.imshow('RED ENDS shown WHITE',forRedAndShot)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	print (pockets)
	#print colorRed
	print (colorBlack)
	print (colorWhite)
	#print rangeRedEnd
	print (rangeB)
	print (rangeW)
	print (square)
	#print redEnds
	print (radius)
	print (striker_radius)
	print (strikerLine_y)
	print (strikerLineEnds)
	print (strikerLine_Start)
	print (strikerLine_End)


#once calibrated, set flag
calib=0

while True :
	while(buttonPress!='1') :
		buttonPress=ser.read()
		print ('trigger awaited')
		
	#declare default camera object
	cap = cv2.VideoCapture(1)
	time.sleep(1)
	# Capture a frame
	ret, p = cap.read()
	#release the resource
	cap.release()

	#p=cv2.imread('DirectShot2.jpg',-1)
	#j is grayscale, p is color(RGB), q is color(HSV)
	j=cv2.cvtColor(p,cv2.COLOR_BGR2GRAY)
	q=cv2.cvtColor(p,cv2.COLOR_BGR2HSV)
	q=cv2.medianBlur(q,11)
	j=cv2.medianBlur(j,5)
	centrej=cv2.cvtColor(j,cv2.COLOR_GRAY2RGB)
	
	#find circles using the Hough Transform
	circles=cv2.HoughCircles(j,cv2.CV_HOUGH_GRADIENT,1,minD,param1=p1,param2=p2,minRadius=minR,maxRadius=maxR)
	circles=np.uint16(np.around(circles))
	circlesW=[]
	circlesB=[]
	ref=[]

	#show circles in green and centres in red
	#also classify coins based on the colors at their centres(values by calib)
	for i in circles[0, :] :
		cv2.circle(centrej,(i[0],i[1]),i[2],(0,255,0),2)
		cv2.circle(centrej,(i[0],i[1]),2,(0,0,255),3)
		if i[0]>(square[3][1]+pocketParam) or i[0]<(square[0][1]-pocketParam) :
			pass # Ignore circles outside the left/right boundaries
		elif i[1]<(square[0][0]-pocketParam) or i[1]>(square[1][0]+pocketParam) :
			pass # Ignore circles outside the top/bottom boundaries
		
		elif q[i[1],i[0],1]>rangeB[1][1] and q[i[1],i[0],1]<rangeB[0][1] and q[i[1],i[0],0]>rangeB[1][0] and q[i[1],i[0],0]<rangeB[0][0]:
			circlesB.append([i[1]-square[0][0],i[0]-square[0][1]])
			radius+=i[2]
		elif q[i[1],i[0],1]>rangeW[1][1] and q[i[1],i[0],1]<rangeW[0][1] and q[i[1],i[0],0]>rangeW[1][0] and q[i[1],i[0],0]<rangeW[0][0]:
			circlesW.append([i[1]-square[0][0],i[0]-square[0][1]])
			radius+=i[2]
		else :
			ref.append([i[1]-square[0][0],i[0]-square[0][1]]) #circle does not match black or white
	cv2.imshow('DETECTED circles and centres',centrej)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	print (redEnds)
	print (circlesW)
	print (circlesB)
	for i in circlesW :
		cv2.circle(centrej,(i[1],i[0]),2,(255,255,255),3)
	for i in circlesB :
		cv2.circle(centrej,(i[1],i[0]),2,(255,0,0),3)
	for i in ref :
		cv2.circle(centrej,(i[1],i[0]),2,(0,255,0),3)
	cv2.imshow('CLASSIFIED: With their colors',centrej)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	

	listOfWhiteCoins=[]
	listOfBlackCoins=[]
	listOfRedCoins=[]
	listofShootableCoins=[]

	#amalgamating image processing with AI shot model
	for i in circlesB :
			temp=BlackCoin(i[1],i[0])
			listOfBlackCoins.append(temp)
	for i in circlesW :
			temp=WhiteCoin(i[1],i[0])
			listOfWhiteCoins.append(temp)

	
	Y=int(strikerLine_y)
	for coin in listOfBlackCoins:
		boold,x,angle,power = directShot(coin)
		if(boold):
			print("Attempt a shot from position"+ str(x)+" and angle "+str(angle))
			X=int(x)
			X2=coin.getx()
			Y2=coin.gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
			listofShootableCoins.append([coin,0])
		else:
			boolc,x,angle,power=cutShot(coin);
			if(boolc):
				print("Attempt a cut shot from position"+ str(x)+" and angle "+str(angle))
				X=int(x)
				X2=coin.getx()
				Y2=coin.gety()
				cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
				listofShootableCoins.append([coin,1])
			else:
				bools,x,angle,power=sideCollideShot(coin);
				if(bools):
					print("Attempt a side shot from position"+ str(x)+" and angle "+str(angle))
					X=int(x)
					X2=coin.getx()
					Y2=coin.gety()
					cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
					#cv2.line(centrej,(X+square[0][1],Y+square[0][0]),(X2+square[0][1],Y2+square[0][0]),(0,0,255),thickness=4)
					listofShootableCoins.append([coin,2])
				else:
					print("No viable shot found!")
    
	for coin in listOfWhiteCoins:
		boold,x,angle,power = directShot(coin)
		if(boold):
			print("Attempt a shot from position"+ str(x)+" and angle "+str(angle))
			X=int(x)
			X2=coin.getx()
			Y2=coin.gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
			listofShootableCoins.append([coin,0])
		else:
			boolc,x,angle,power=cutShot(coin);
			if(boolc):
				print("Attempt a cut shot from position"+ str(x)+" and angle "+str(angle))
				X=int(x)
				X2=coin.getx()
				Y2=coin.gety()
				cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
				listofShootableCoins.append([coin,1])
			else:
				bools,x,angle,power=sideCollideShot(coin);
				if(bools):
					print("Attempt a side shot from position"+ str(x)+" and angle "+str(angle))
					X=int(x)
					X2=coin.getx()
					Y2=coin.gety()
					cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
					#cv2.line(centrej,(X+square[0][1],Y+square[0][0]),(X2+square[0][1],Y2+square[0][0]),(0,0,255),thickness=4)
					listofShootableCoins.append([coin,2])
				else:
					print("No viable shot found!")

	for coin in listOfRedCoins:
		boold,x,angle,power = directShot(coin)
		if(boold):
			print("Attempt a shot from position"+ str(x)+" and angle "+str(angle))
			X=int(x)
			X2=coin.getx()
			Y2=coin.gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
			listofShootableCoins.append([coin,0])
		else:
			boolc,x,angle,power=cutShot(coin);
			if(boolc):
				print("Attempt a cut shot from position"+ str(x)+" and angle "+str(angle))
				X=int(x)
				X2=coin.getx()
				Y2=coin.gety()
				cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
				listofShootableCoins.append([coin,1])
			else:
				bools,x,angle,power=sideCollideShot(coin);
				if(bools):
					print("Attempt a side shot from position"+ str(x)+" and angle "+str(angle))
					X=int(x)
					X2=coin.getx()
					Y2=coin.gety()
					cv2.line(centrej,(X,Y),(X2,Y2),(0,0,255),thickness=4)
					#cv2.line(centrej,(X+square[0][1],Y+square[0][0]),(X2+square[0][1],Y2+square[0][0]),(0,0,255),thickness=4)
					listofShootableCoins.append([coin,2])
				else:
					print("No viable shot found!")

	
	#deciding one shot
	for i in listofShootableCoins:
		if i[1]==0:
			boold,x,angle,power = directShot(i[0])
			print("Best shot from position "+ str(x)+" from angle "+str(angle))
			X=int(x)
			X2=i[0].getx()
			Y2=i[0].gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,255,0),thickness=4)
			break
		elif i[1]==1:
			boold,x,angle,power = cutShot(i[0])
			print("Best shot from position "+ str(x)+" from angle "+str(angle))
			X=int(x)
			X2=i[0].getx()
			Y2=i[0].gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,255,0),thickness=4)
			break
		elif i[1]==2:
			boolc,x,angle,power=sideCollideShot(coin)
			print("Best shot from position "+ str(x)+" from angle "+str(angle))
			X=int(x)
			X2=i[0].getx()
			Y2=i[0].gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,255,0),thickness=4)
			break
		else:
			boolx=True
			x=randint(strikerLine_Start+0.1*(strikerLine_End-strikerLine_Start),strikerLine_End-0.1*(strikerLine_End-strikerLine_Start))
			j=randint(0,len(listOfBlackCoins)-1)
			angle=degrees(atan((listOfBlackCoins[j].gety-strikerLine_y)/(float(listOfBlackCoins[j].gety-x))))
			print("Random shot from position "+ str(x)+" from angle "+str(angle))
			X=int(x)
			X2=i[0].getx()
			Y2=i[0].gety()
			cv2.line(centrej,(X,Y),(X2,Y2),(0,255,0),thickness=4)
			power=200

	#showing the decided shot
	cv2.imshow('Decided Shot',centrej)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	#representing distance as a fraction between start and end point
	#will be multiplied by actual physical distance in Arduino Code
	distance=x-strikerLine_Start
	distance=distance/float(strikerLine_End-strikerLine_Start)
	distanceInt=int(100*distance)
	angleInt=int(angle)
	powerInt=int(power)
	print (distanceInt)
	print (angleInt)

	#Serial pcommunication to arduino
	if angleInt < 100 or distanceInt<10:
		if angleInt<100 and distanceInt<10:
			ser.write(str(0)+str(distanceInt)+str(0)+str(angleInt)+str(powerInt))
			print (str(0)+str(distanceInt)+str(0)+str(angleInt)+str(powerInt))
		elif distanceInt<10:
			ser.write(str(0)+str(distanceInt)+str(angleInt)+str(powerInt))
			print (str(0)+str(distanceInt)+str(angleInt)+str(powerInt))
		else:
			ser.write(str(distanceInt)+str(0)+str(angleInt)+str(powerInt))		
			print (str(distanceInt)+str(0)+str(angleInt)+str(powerInt))
	else:
		ser.write(str(distanceInt)+str(angleInt)+str(powerInt))
		print (str(distanceInt)+str(angleInt)+str(powerInt))
	
	buttonPress=ser.read()
