import sys
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
class image_converter:
    def __init__(self):
        self.image_pub = rospy.Publisher("auv/cv/path",Image)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("auv/sensors/cam_down",Float64MultiArray, queue_size=10, self.callback) 
    
    def callback(self,data):
        '''
        input: ros image from the subscriber "auv/sensors/cam_down"
        output: errors from converting cv_image to ros_images & vice versa and publishes data to "auv/cv/path"
        '''
        # converting ROS image to cv_image 
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
             
        except CvBridgeError as e:
            print(e)
                
        # converting pixels of the image to hsv from rgb
        into_hsv =(cv2.cvtColor(cv_image,cv2.COLOR_BGR2HSV))
        L_limit=np.array([8, 25, 50]) 
        U_limit=np.array([30, 255, 255]) 
            
    
        orange=cv2.inRange(into_hsv,L_limit,U_limit)

        kernel = np.ones((5, 5), np.uint8)
        orange = cv2.morphologyEx(orange, cv2.MORPH_OPEN, kernel)

        orange = cv2.GaussianBlur(orange, (11,11), 0)
        ret, thresh = cv2.threshold(orange, 230, 255, cv2.THRESH_BINARY)
        
        blur = cv2.blur(thresh, (10,10))

        ret2, thresh2 = cv2.threshold(blur, 1, 255, cv2.THRESH_OTSU)
        contours, heirarchy = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        edges = cv2.Canny(image=thresh2, threshold1=100, threshold2=200)
        
        c = max(contours, key = cv2.contourArea)
        cv2.drawContours(frame, c, -1, 255, 3)

        cv2.waitKey(3)

        # publish the data to "auv/cv/path"
        try:
            # self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8")) 
            # this would convert cv imge back to a ROS image, can uncomment to get visual display of the contours drawn 
            self.image_pub.publish(c)

        except CvBridgeError as e:
            print(e) # prints errors if any occured in converting cv_image to ros_image or vice versa

    def main(args):
        '''
        input: none
        output: none
        executes callback() and init() functions
        ic is the object the class is executed as
        '''
        ic = image_converter() # initializes the class as the object ic  
        rospy.init_node('image_converter', anonymous=True) # initializing ros node
        
        try:
            rospy.spin() # keeps your node from exiting until the node has been shutdown callback is invoked with the message as the first argument.
            
        except KeyboardInterrupt:
            print("Shutting down")
            cv2.destroyAllWindows()

    if __name__ == '__main__':
        main(sys.argv)
